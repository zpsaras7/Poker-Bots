from deuces import Card
from deuces import Evaluator
import matplotlib.pyplot as plt

class HandStrength:
    source = "www.natesholdem.com/pre-flop-odds.php#Top"

    def __init__(self, myHand):
        self.first_card = Card.int_to_str(myHand[0])
	self.second_card = Card.int_to_str(myHand[0])
	suited = checkSuited()
	pair = checkPair()
	closeness_points = getCloseness()
	highest_card_points = getHighCardPoints()

    def checkSuited(self):
	if self.first_card[1] == self.second_card[1]:
	    return True
	else:
	    return False

    def checkPair(self):
        if self.first_card[0] == self.second_card[0]:
	    return True
	else:
	    return False
    
    def number_to_points(self, card):
        if card[0] == 'A':
	    return 10
	elif card[0] == 'K':
	    return 8
	elif card[0] == 'Q':
	    return 7
	elif card[0] == 'J':
	    return 6
	elif card[0] == 'T':
	    return 5
	else:
	    return int(card[0])/2.0

    def getHighCardPoints(self):
	return max(self.number_to_points(self.first_card), self.number_to_points(self.second_card))
