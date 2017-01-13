import argparse
import socket
import sys

from deuces import Card
from deuces import Evaluator
import matplotlib.pyplot as plt

"""
Simple example pokerbot, written in python.

This is an example of a bare bones pokerbot. It only sets up the socket
necessary to connect with the engine and then always returns the same action.
It is meant as an example of how a pokerbot should communicate with the engine.
"""
class Player:
    current_hand = []
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

            # Here is where you should implement code to parse the packets from
            # the engine and act on it. We are just printing it instead.
            print data

            # When appropriate, reply to the engine with a legal action.
            # The engine will ignore all spurious responses.
            # The engine will also check/fold for you if you return an
            # illegal action.
            # When sending responses, terminate each response with a newline
            # character (\n) or your bot will hang!
            words = data.split()
            packetName = data.split()[0]
            if packetName == "GETACTION":
                potSize = words[1]
                numBoardCards = words[2]
                boardCards = [] if numBoardCards == 0 else words[3:3+numBoardCards]
                
                words = words[4+numBoardCards:-1]
                numLastActions = words[0]
                lastActions = [] if numLastActions == 0 else words[1 : 1+numLastActions]
               
                words = words[2+numLastActions:-1]
                numLegalActions = words[0]
                legalActions = [] if numLegalActions == 0 else words[1 : 1+numLegalActions]
                
                timebank = words[-1]
                # Currently CHECK on every move. You'll want to change this.
                s.send("CHECK\n")
            elif packetName == "NEWHAND":
                handId = words[1]
                button = words[2] == 'True'
                hand = [ words[3], words[4]]
                current_hand = [ Card.new(handCardString) for handCardString in hand]
                print "hand:", hand, " ; set current_hand to ", current_hand
                myBank = words[5]
                otherBank = words[6]
                timeBank = words[-1]
            elif packetName == "HANDOVER":
                print "Hand over; "
            elif packetName == "REQUESTKEYVALUES":
                print "Could write some key value pairs...", i
                i+= 1
                # At the end, the engine will allow your bot save key/value pairs.
                # Send FINISH to indicate you're done.
                s.send("FINISH\n")
        # Clean up the socket.
        s.close()

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
