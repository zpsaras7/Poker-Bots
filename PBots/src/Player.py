import argparse
import socket

from deuces import Card
from deuces import Evaluator
import matplotlib.pyplot as plt
import random
from HandStrength import HandStrength

import Recorder as rec
import ActionQueue as aq


global evaluator
global recorder
global actionQueue

evaluator = Evaluator()
recorder = rec.Recorder()
actionQueue = aq.ActionQueue()

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
                print words
                index = 3  #index of next word to look up / handle; avoids resizing words list
                boardCards = [Card.new(cardString) for cardString in words[index:index+numBoardCards] ]
                index+= numBoardCards

                numLastActions = int(words[index])
                index+= 1
                lastActions = words[index : index+numLastActions]
                index+= numLastActions
               
                numLegalActions = int(words[index])
                index+= 1
                legalActions = words[index : index+numLegalActions]
                index+= numLegalActions
                
                self.setTimeBankSeconds(words[-1])

                self.handleAction(potSize, boardCards, lastActions, legalActions)

            elif packetName == "HANDOVER":
                win = False
                for w in words:
                    if "WIN" in w and self.matchParameters['my_name'] in w:
                        #print "Won hand with confidences: ", self.currentConfidence
                        win = True
                #if not win:
                    #print "Lost hand with confidences: ", self.currentConfidence
                print words
                self.currentConfidence = []
                #recorder.recordGame(self.currentParameters['handID'], false)
            elif packetName == "REQUESTKEYVALUES":
                print "Could write some key value pairs...", i
                i+= 1
                # At the end, the engine will allow your bot save key/value pairs.
                # Send FINISH to indicate you're done.
                s.send("FINISH\n")
        # Clean up the socket.
        s.close()
        
    def handleAction(self, potSize, boardCards, lastActions, legalActions):
        '''
        Logic for deciding what action to respond with given the most recent GETACTION packet
        '''
        #recorder.write('handleAction(); board cards ', boardCards)
        
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
        recorder.write('handRank:'+ str(handRankDec))
        self.currentConfidence.append(handRankDec)
        #legalActionQueue = ActionQueue(legalActions)
        decidedAction = None
        defaultAction = 'FOLD'

        actionParamsList = [actionQueue.analyzeActionString(action)[1] for action in legalActions]

        if handRankDec < .3: #above average hand or random bluff
            for params in actionParamsList:
                if params['type'] == 'LEGAL_A':
                    decidedAction = params['name'] + ':'+str(int(params['min'] + (params['max'] - params['min'])*handRankDec))
                    s.send(decidedAction+'\n')
                    return
            for params in actionParamsList:
                if params['type'] == 'LEGAL_B':
                    if 'C' in params['name']: #either check or call
                        decidedAction = params['name']
                        s.send(decidedAction+'\n')
                        return
        elif handRankDec >= .3 and handRankDec < .8:
            for params in actionParamsList:
                try:
                    if self.currentParameters['haveButton']:
                        if params['type'] == 'LEGAL_B':
                            if 'C' in params['name']:
                                decidedAction = params['name']
                                s.send(decidedAction+'\n')
                                return
                    elif random.random() < .5:
                        if params['type'] == 'LEGAL_B':
                            if 'C' in params['name']:
                                decidedAction = params['name']
                                s.send(decidedAction+'\n')
                                return
                        elif params['type'] == 'LEGAL_A':
                            decidedAction = params['name'] + ':'+str(int(params['min'] + (params['max'] - params['min'])*handRankDec))
                            s.send(decidedAction+'\n')
                            return
                except:
                    print "******************************", params
                    continue
                    
        elif handRankDec >= .8: #below average hand
            for params in actionParamsList:
                if params['type'] == 'LEGAL_B':
                    if 'CHECK' in params['name']:
                        decidedAction = params['name']
                        s.send(decidedAction+"\n")
                        return
            s.send(defaultAction+'\n')
            return
        if decidedAction is None:
            #go with default action (maybe make this random)
            #recorder.write('decidedAction is None; sending:', defaultAction)
            s.send(defaultAction+'\n')
        
    def setTimeBankSeconds(self, newTimeStr):
        #Updates the current time remaining
        self.currentParameters['remaining_time_ms'] = float(newTimeStr)*1000
        
    def handleActionPreFlop(self, potSize, lastActions, legalActions, cutoff=5.0):
        if len(legalActions) == 1:
            print "taking automatic action; only legal action is:", legalActions[0]
            s.send(legalActions[0]+'\n')
            return 
        strength = HandStrength(self.currentParameters['hand'])
        actionParamsList = [actionQueue.analyzeActionString(action)[1] for action in legalActions]
        #print strength.chen_score
        if strength.chen_score >= cutoff:
            for params in actionParamsList:
                if params['type'] == 'LEGAL_A':
                    decidedAction = params['name'] + ':'+str(int(params['min'] + (params['max'] - params['min'])*(strength.chen_score/20.)/2))
                    s.send(decidedAction+'\n')
                    return
            for params in actionParamsList:
                if params['type'] == 'LEGAL_B':
                    if 'C' in params['name']: #either check or call
                        decidedAction = params['name']
                        s.send(decidedAction+'\n')
                        return
        else:
            for params in actionParamsList:
                if params['type'] == 'LEGAL_B':
                    if 'CHECK' in params['name']:
                        decidedAction = params['name']
                        s.send(decidedAction+"\n")
                        return
            s.send('FOLD\n')
            return

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
