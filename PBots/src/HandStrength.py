from deuces import Card
from deuces import Evaluator
import matplotlib.pyplot as plt

class HandStrength:
    source = "holdem wiki --> chen formula"
    def __init__(self, myHand):
        self.first_card = Card.int_to_str(myHand[0])
	self.second_card = Card.int_to_str(myHand[1])
	suited = self.checkSuited()
	pair = self.checkPair()
	closeness_points = self.getCloseness()
	highest_card_points = self.getHighCardPoints()
	self.chen_score = self.getChenScore(highest_card_points, pair, suited, closeness_points)

    def cardToInt(self, card):
	if card[0] == 'A':
	    return 14
	elif card[0] == 'K':
	    return 13
	elif card[0] == 'Q':
	    return 12
	elif card[0] == 'J':
	    return 11
	elif card[0] == 'T':
	    return 10
	else:
	    return int(card[0])

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

    def getHighCardPoints(self):
	return max(self.number_to_points(self.first_card), self.number_to_points(self.second_card))

    def getCloseness(self):
	distance = abs(self.cardToInt(self.first_card) - self.cardToInt(self.second_card))
        if distance == 3:
	    return 4
	elif distance > 3:
	    return 5
	else:
	    return distance

    def getChenScore(self, high_card, p, s, closeness):
	score = high_card
	if p:
	    score = score*score
        else:
	    if s:
	        score += 2
            score -= closeness
        return score
	
