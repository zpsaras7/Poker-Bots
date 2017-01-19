import Queue

from deuces import Card

global debug
debug = False

global ACTION_LIST_A
ACTION_LIST_A = ['BET', 'RAISE']

global ACTION_LIST_B
ACTION_LIST_B = ['CALL', 'CHECK', 'FOLD']

global ACTION_LIST_C
ACTION_LIST_C = [ 'POST', 'REFUND', 'TIE', 'WIN']

'''
Wrapper class for a Synchronous queue to hold and parse Actions tokens 
from the server. 
(see http://mitpokerbots.com/docs/grammar.html#legalactions
for documentation of all possible actions)
'''
class ActionQueue:
    global debug
    global ACTION_LIST_B
    global ACTION_LIST_A
    global ACTION_LIST_C
    
    queue = Queue.Queue()
    
    def __init__(self, *actionList):
        if actionList:
            if isinstance(actionList[0], str):
                for x in actionList:
                    self.queue.put(x)
            elif isinstance(actionList[0], list):
                for x in actionList[0]:
                    self.queue.put(x)
    
    def addAction(self, actionString):
        self.queue.put(actionString)
        
    def getNextAction(self):
        return self.queue.get()
    
    #def getNextOpponentAction(self):
    #    act = self.getNextAction()
        
    def analyzeActionString(self, actionStr):
        if(debug):
            print "analyzeActionString() on ", actionStr
        tokens = actionStr.split(':')
        actionName = tokens[0]
        actionParams = { 'name' : tokens[0] }
        
        if actionName in ACTION_LIST_A: #bet, raise
            if len(tokens) == 2: #performed action (with actor missing)
                actionParams['type'] = 'PERFORMED'
                actionParams['amount'] = int(tokens[1])
            elif tokens[2].isdigit(): #legal action with min/max
                actionParams['type'] = 'LEGAL_A'
                actionParams['min'] = int(tokens[1])
                actionParams['max'] = int(tokens[2])
            else: #performed action with actor present
                actionParams['type'] = 'PERFORMED'
                actionParams['amount'] = int(tokens[1])
                actionParams['actor'] = tokens[2]
        elif actionName in ACTION_LIST_B: #call, check, fold
            if len(actionParams) == 2:
                actionParams['type'] = 'PERFORMED'
                actionParams['actor'] = tokens[1]
            else:
                actionParams['type'] = 'LEGAL_B'
        elif actionName in ACTION_LIST_C: #post, refund, tie, win
            actionParams['type'] = 'PERFORMED'
            actionParams['amount'] = int(tokens[1])
            actionParams['actor'] = tokens[2]

        elif actionName == 'DISCARD':
            actionParams['type'] = 'PERFORMED' #I'm not sure  you can tell 
            actionParams['actor'] = tokens[1]
        elif actionName == 'DEAL':
            actionParams['type'] = 'PERFORMED'
            actionParams['street'] = tokens[1] #FLOP, TURN or RIVER
        elif actionName == 'SHOW':
            actionParams['type'] = 'PERFORMED'
            actionParams['cards'] = [Card.new(cardStr) for cardStr in tokens[1:5]]
            actionParams['actor'] = tokens[5]
         
        #print 'analysis complete; returning ', (actionStr, actionParams)
        return (actionStr, actionParams)
        
    def clear(self):
        self.queue = Queue.Queue()