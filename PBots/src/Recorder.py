from deuces import Card
from deuces import Evaluator

'''
For recording specific game information to a separate file
than the verbose player dump files.
'''

class Recorder:
    fileName = 'recorder.txt'
    
    def __init__(self, *outputFileName):
        if outputFileName:
            self.fileName = outputFileName[0]
        outputFile = open(self.fileName, 'w')
        outputFile.close()
        
    def recordGame(self, gameID, win):
        output = 'gameID:'
        output+= str(gameID)
        output+= '|win:'
        output+= str(win)
        self.write(output)
        
    def write(self, stringToWrite):
        outputFile = open(self.fileName, 'w')
        outputFile.write(stringToWrite)
        outputFile.close()