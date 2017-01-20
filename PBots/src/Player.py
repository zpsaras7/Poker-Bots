import argparse
import socket

from deuces import Card
from deuces import Evaluator
from Historian import Historian
#import matplotlib.pyplot as plt
import random
from HandStrength import HandStrength

import Recorder as rec
from actionQueue import ActionQueue
#from ctypes.wintypes import WORD


global evaluator
global recorder
#global actionQueue

evaluator = Evaluator()
recorder = rec.Recorder()
#actionQueue = aq.ActionQueue()

class Player:
    matchParameters = {'my_name' : '', 
                       'opponent_name':'',
                       'stackSize':0,
                       'bb':0,
                       'numHands':0}
    currentParameters = {'handID':None,
                         'hand':[], 
                         'haveButton':False,
                         'remaining_time_ms':1000}
    
    currentConfidence = None

    def run(self, input_socket):
        # Get a file-object for reading packets from the socket.
        # Using this ensures that you get exactly one packet per read.
        f_in = input_socket.makefile()
        i=0
        self.currentConfidence = []
        while True:
            # Block until the engine sends us a packet.
            data = f_in.readline().strip()
            # If data is None, connection has closed.
            if not data:
                print "Gameover, engine disconnected."
                break

            # When appropriate, reply to the engine with a legal action.
            # The engine will ignore all spurious responses.
            # The engine will also check/fold for you if you return an
            # illegal action.
            # When sending responses, terminate each response with a newline
            # character (\n) or your bot will hang!
            words = data.split()
            packetName = data.split()[0]
            #print "SOCKET_WORDS: ", words
            
            if packetName == 'NEWGAME':
                self.matchParameters['my_name'] = words[1]
                self.matchParameters['opponent_name'] = words[2]
                self.matchParameters['stackSize'] = int(words[3])
                self.matchParameters['bb'] = int(words[4])
                self.matchParameters['numHands'] = int(words[5])
                self.setTimeBankSeconds(words[-1])
                self.historian = Historian(self.matchParameters['opponent_name'], self.matchParameters['my_name'], self.matchParameters['bb'])
            elif packetName == "NEWHAND":
                self.currentParameters['handID'] = words[1]
                self.currentParameters['haveButton'] = True if words[2] == 'true' else False
                self.currentParameters['hand'] = [ Card.new(words[3]), Card.new(words[4]) ]
                self.currentParameters['myBank'] = int(words[5])
                self.currentParameters['opponentBank'] = int(words[6])
                self.setTimeBankSeconds(words[-1])
            elif packetName == "GETACTION":
                potSize = words[1] # how much pot there is currently
                numBoardCards = int(words[2])
                
                index = 3  #index of next word to look up / handle; avoids resizing words list
                boardCards = [Card.new(cardString) for cardString in words[index:index+numBoardCards] ]
                index+= numBoardCards

                numLastActions = int(words[index])
                index+= 1
                lastActions = words[index : index+numLastActions]
                self.historian.update([ActionQueue.analyzeActionString(action)[1] for action in lastActions])
                index+= numLastActions
               
                numLegalActions = int(words[index])
                index+= 1
                legalActions = words[index : index+numLegalActions]
                index+= numLegalActions
                self.setTimeBankSeconds(words[-1])

                self.handleAction(potSize, boardCards, lastActions, legalActions)

            elif packetName == "HANDOVER":
                win = False
                self.historian.update([ActionQueue.analyzeActionString(action)[1] for action in words])
                for w in words:
                    if "WIN" in w and self.matchParameters['my_name'] in w:
                        #print "Won hand with confidences: ", self.currentConfidence
                        win = True
                #if not win:
                    #print "Lost hand with confidences: ", self.currentConfidence
                self.currentConfidence = []
                #recorder.recordGame(self.currentParameters['handID'], false)
            elif packetName == "REQUESTKEYVALUES":
                i+= 1
                # At the end, the engine will allow your bot save key/value pairs.
                # Send FINISH to indicate you're done.
                s.send("FINISH\n")
        print self.matchParameters['opponent_name'], "**************"
        print "PFR: ", self.historian.getPFR()
        print "CallRaise: ", self.historian.getCallRaise()
        print "CheckRaise: ", self.historian.getCheckRaise()
        print "2Bet: ", self.historian.get2BetRate()
        print "3Bet: ", self.historian.get3BetRate()
        print "Aggression: ", self.historian.getAgression()
        print "Aggression Freq: ", self.historian.getAggroFreq()
        print "Hands Played: ", self.historian.num_hands_played
        print "Flops Seen: ", self.historian.seen_flop_count
        print "Showdowns: ", self.historian.showdown_count
        # Clean up the socket.
        s.close()
        
    def handleAction(self, potSize, boardCards, lastActions, legalActions):
        '''
        Logic for deciding what action to respond with given the most recent GETACTION packet
        '''
        #recorder.write('handleAction(); board cards ', boardCards)
        acceptableActions = ActionQueue(legalActions[0], 1000) #starts with default action with lowest priority
        
        if len(legalActions) == 1:
            print "taking automatic action; only legal action is:", legalActions[0]
            s.send(legalActions[0]+'\n')
            return 
        if len(boardCards) == 0:
            self.handleActionPreFlop(potSize, lastActions, legalActions)
            return
        else:
            handRank = evaluator.evaluate(self.currentParameters['hand'], boardCards)
        handRankDec = evaluator.get_five_card_rank_percentage(handRank)
        print "LEGAL", legalActions
        self.currentConfidence.append(handRankDec)
        legalActionParamsList = [ActionQueue.analyzeActionString(action)[1] for action in legalActions]
        if handRankDec < .3: #above average hand or random bluff
            print "Above avg hand (", handRankDec,')'     
            for legalActionParams in legalActionParamsList:
                if legalActionParams['type'] == 'LEGAL_A':
                    _max = legalActionParams['max']
                    _min = legalActionParams['min']
                    a = legalActionParams['name'] + ':'+str(int( _min + (_max - _min)*(1. - handRankDec) )) #bet higher w/ lower handRankDec
                    acceptableActions.addAction(a, 0) # high priority in p queue
                    print "\tAdded acceptable action[0]:", a, '\n\tAcceptable:', acceptableActions.getStringForPrinting(2)
                elif legalActionParams['name'] == 'CALL' or legalActionParams['name'] == 'CHECK':
                    a = legalActionParams['name']
                    acceptableActions.addAction( a, 1 )
                    print "\tAdded acceptable action[1]:", a, '\n\tAcceptable:', acceptableActions.getStringForPrinting(2)
                
        elif handRankDec >= .3 and handRankDec < .8:
            print "Medium hand (", handRankDec,')'
            _random = random.random() # grab a random number before iterating to be consistent with 1 set of rules
            for legalActionParams in legalActionParamsList:
                if self.currentParameters['haveButton']: #CALL or CHECK if dealer 
                    if legalActionParams['name'] == 'CHECK' or legalActionParams['name'] == 'CALL':
                        a = legalActionParams['name']
                        acceptableActions.addAction( a, 1 )
                        print "\tAdded acceptable action[2]:", a, '\n\tAcceptable:', acceptableActions.getStringForPrinting(2)
                        
                    elif _random < .2 and legalActionParams['type'] == 'LEGAL_A': #sometimes bet with button
                        _max = legalActionParams['max']
                        _min = legalActionParams['min']
                        # with the button and this hand, don't bet near max when betting
                        _max-= int((_max - _min) / 2.)
                        a = legalActionParams['name'] + ':'+str(int( _min + (_max - _min)*(1. - handRankDec) ))
                        acceptableActions.addAction( a, 0 ) # 
                        print "\tAdded acceptable action[3]:", a, '\n\tAcceptable:', acceptableActions.getStringForPrinting(2)
                            
                #Be aggressive with this type of hand some of the time
                elif not self.currentParameters['haveButton'] and _random > handRankDec:
                    if legalActionParams['type'] == 'LEGAL_A':
                        _max = legalActionParams['max']
                        _min = legalActionParams['min']
                        
                        # reduce max bet so opponent can't correlate our bets to our handRank as easily
                        potential = int(_max - _random * (_max - _min)) #compute a semi-random amount and check it for validity
                        if(potential < legalActionParams['min'] or potential > legalActionParams['max']):
                            potential = legalActionParams['min']
                            
                        a = legalActionParams['name'] + ':'+str(potential)
                        acceptableActions.addAction( a, 0) 
                        print "\tAdded acceptable action[4]:", a, '\n\tAcceptable:', acceptableActions.getStringForPrinting(2)
                            
                    elif legalActionParams['name'] == 'CHECK' or legalActionParams['name'] == 'CALL':
                        a = legalActionParams['name']
                        acceptableActions.addAction( a, 1 )
                        print "\tAdded acceptable action[5]:", a, '\n\tAcceptable:', acceptableActions.getStringForPrinting(2)
        
        elif handRankDec >= .8: #below average hand
            print "shitty hand (", handRankDec,')'
            for legalActionParams in legalActionParamsList:
                if legalActionParams['type'] == 'LEGAL_B':
                    #Try to FOLD if possible
                    if legalActionParams['name'] == 'FOLD':
                        a = legalActionParams['name']
                        acceptableActions.addAction( a, 0 )
                        print "\tAdded acceptable action[6]:", a, '\n\tAcceptable:', acceptableActions.getStringForPrinting(2)

                    elif legalActionParams['name'] == 'CHECK':
                        a = legalActionParams['name']
                        acceptableActions.addAction( a, 1 )
                        print "\tAdded acceptable action[7]:", a, '\n\tAcceptable:', acceptableActions.getStringForPrinting(2)
                        
                elif legalActionParams['type'] == 'LEGAL_A':
                    #Do the min if have to bet/raise
                    a = legalActionParams['name'] + ':'+str(legalActionParams['min'])
                    acceptableActions.addAction( a, 5 ) 
                    print "\tAdded acceptable action[8]:", a, '\n\tAcceptable:', acceptableActions.getStringForPrinting(2)
            
        if len(acceptableActions) > 0:
            #Got some acceptable action responses; choose one:
            #TODO: choose 2nd best with low probability?
            decidedAction = acceptableActions.getNextAction()
            print "Sending Action:", decidedAction
            s.send(decidedAction+"\n")
        else:
            print "ERROR", legalActions
            s.send(legalActions[0]+"\n")
        
    def setTimeBankSeconds(self, newTimeStr):
        #Updates the current time remaining
        self.currentParameters['remaining_time_ms'] = float(newTimeStr)*1000
        
    def handleActionPreFlop(self, potSize, lastActions, legalActions, cutoff=7.0):
        if len(legalActions) == 1:
            print "taking automatic action; only legal action is:", legalActions[0]
            s.send(legalActions[0]+'\n')
            return 
        acceptableActions = ActionQueue(legalActions[0], 1000) #starts with default action with lowest priority
        
        strength = HandStrength(self.currentParameters['hand'])
        actionParamsList = [ActionQueue.analyzeActionString(action)[1] for action in legalActions]
        if strength.chen_score >= cutoff and random.random() < .8:
            for params in actionParamsList:
                if params['type'] == 'LEGAL_A':
                    a = params['name'] + ':'+str(int(params['min'] + (params['max'] - params['min'])*(strength.chen_score/20.)/2))
                    acceptableActions.addAction( a, 0 )
                if params['type'] == 'LEGAL_B':
                    if 'C' in params['name']: #either check or call
                        acceptableActions.addAction(params['name'], 1)
            decidedAction = acceptableActions.getNextAction()
            print "Sending Action:", decidedAction
            s.send(decidedAction+"\n")
        else: ##don't be betting
            for params in actionParamsList:
                if params['type'] == 'LEGAL_A': #bet if legally obligated 
                    a = params['name'] + ':'+str(params['min'])
                    acceptableActions.addAction( a, 10 )
                elif params['type'] == 'LEGAL_B':
                    if 'CHECK' in params['name']:
                        acceptableActions.addAction(params['name'], 0)
                    else:
                        acceptableActions.addAction(params['name'], 1)
                        
            decidedAction = acceptableActions.getNextAction()
            print "Sending Action:", decidedAction
            s.send(decidedAction+"\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A Pokerbot.', add_help=False, prog='pokerbot')
    parser.add_argument('-h', dest='host', type=str, default='localhost', help='Host to connect to, defaults to localhost')
    parser.add_argument('port', metavar='PORT', type=int, help='Port on host to connect to')
    args = parser.parse_args()

    # Create a socket connection to the engine.
    print 'Connecting to %s:%d' % (args.host, args.port)
    try:
        s = socket.create_connection((args.host, args.port))
    except socket.error as e:
        print 'Error connecting! Aborting'
        exit()

    bot = Player()
    bot.run(s)
