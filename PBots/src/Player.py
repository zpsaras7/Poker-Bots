import argparse
import socket
import sys

from deuces import Card
from deuces import Evaluator
import matplotlib.pyplot as plt

import Recorder as rec
import ActionQueue as aq

"""
Simple example pokerbot, written in python.

This is an example of a bare bones pokerbot. It only sets up the socket
necessary to connect with the engine and then always returns the same action.
It is meant as an example of how a pokerbot should communicate with the engine.
"""
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

    def run(self, input_socket):
        # Get a file-object for reading packets from the socket.
        # Using this ensures that you get exactly one packet per read.
        f_in = input_socket.makefile()
        i=0
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
                # Currently CHECK on every move. You'll want to change this.
                #s.send("CHECK\n")
            elif packetName == "HANDOVER":
                pass
                #print "Hand over; "
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
        
        handRank = evaluator.evaluate(self.currentParameters['hand'], boardCards)
        handRankDec = evaluator.get_five_card_rank_percentage(handRank)
        recorder.write('handRank:'+ str(handRankDec))
        
        #legalActionQueue = ActionQueue(legalActions)
        decidedAction = None
        defaultAction = 'FOLD'
        
        if handRankDec > .5: #above average hand
            actionParamsList = [actionQueue.analyzeActionString(action)[1] for action in legalActions]
            for params in actionParamsList:
                if params['type'] == 'LEGAL_A':
                    decidedAction = params['name'],':',str(params['min'] + (params['max'] - params['min'])*handRankDec)
                    s.send(decidedAction+'\n')
                    return
                #TODO: finish others
        if handRankDec <= .5: #below average hand
            pass
        if decidedAction is None:
            #go with default action (maybe make this random)
            recorder.write('decidedAction is None; sending:', defaultAction)
            s.send(defaultAction+'\n')
        
    def setTimeBankSeconds(self, newTimeStr):
        #Updates the current time remaining
        self.currentParameters['remaining_time_ms'] = float(newTimeStr)*1000
        
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
