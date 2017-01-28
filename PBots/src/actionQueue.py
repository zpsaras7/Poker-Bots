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
Wrapper class for a Synchronous priority pq to hold and parse Actions tokens 
from the server. 
(see http://mitpokerbots.com/docs/grammar.html#legalactions
for documentation of all possible actions)
'''
class ActionQueue(object):
    global debug
    global ACTION_LIST_B
    global ACTION_LIST_A
    global ACTION_LIST_C
    
    def __init__(self, *actionList):
        self.pq = Queue.PriorityQueue()
        if actionList:
            if isinstance(actionList, tuple): # inputted tuple(s)
                self.addAction(actionList[0], actionList[1])
            elif isinstance(actionList, list): #inputted list of tuples
                for x in actionList:
                    self.addAction(x[0], x[1])
    
    def addAction(self, actionString, priority=0):
        self.pq.put((priority, actionString))
        
    def getNextAction(self):
        return self.pq.get()[1]#return action string
    
    @staticmethod
    def analyzeActionString(actionStr):
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
            if len(tokens) == 2:
                actionParams['type'] = 'PERFORMED'
                actionParams['actor'] = tokens[1]
            else:
                actionParams['type'] = 'LEGAL_B'
                
        elif actionName in ACTION_LIST_C: #post, refund, tie, win
            actionParams['type'] = 'PERFORMED'
            actionParams['amount'] = int(tokens[1])
            actionParams['actor'] = tokens[2]

        elif actionName == 'DISCARD':
            if len(tokens) == 4: # (actor)[3] discarded [1] and got [2]
                actionParams['type'] = 'PERFORMED' 
                actionParams['oldCard'] = tokens[1]
                actionParams['newCard'] = tokens[2]
                actionParams['actor'] = tokens[3]
            elif len(tokens) == 2: # I can discard (card)[1]
                actionParams['type'] = 'LEGAL_D'
                actionParams['discard'] = tokens[1]
                
        elif actionName == 'DEAL':
            actionParams['type'] = 'PERFORMED'
            actionParams['street'] = tokens[1] #FLOP, TURN or RIVER
        elif actionName == 'SHOW':
            actionParams['type'] = 'PERFORMED'
            actionParams['cards'] = [Card.new(cardStr) for cardStr in tokens[1:5]]
            actionParams['actor'] = tokens[5]
         
        #print 'analysis complete; returning ', (actionStr, actionParams)
        return (actionStr, actionParams)
        
    def __len__(self):
        return len(self.pq.queue)
    
    def clear(self):
        self.pq = Queue.PriorityQueue()
        
    def getStringForPrinting(self, indentLevel=1):
        '''
            Debug method to be used for printing the contents of this ActionQueue's actions.
            Slow because re-creates queue every time
        '''
        #print '\tlength BEFORE', len(self)
        pq2 = Queue.PriorityQueue()
        ans = '\n'
        tabBreaker = ''
        for i in range(indentLevel):
            tabBreaker+= '\t'
        
        ls = sorted(list(self.pq.queue))
        for i in range(len(ls)):
            #item = self.pq.get()
            item = ls[i]
            #pq2.put(item)
            #ans+= tabBreaker + str(item[1]) + '\n'
            ans+= tabBreaker + str(item) + '\n'
            
        #self.pq = pq2
        #print "\tlength AFTER", len(self)
        return ans
        