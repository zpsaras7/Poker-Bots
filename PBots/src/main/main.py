#from deuces import Deck
#import ..deuces.Card
#import ..deuces.Evaluator
#import deuces
from deuces import Card
from deuces import Evaluator

W = "Pt"
E = "mc^2"
D = "(b^2-4ac)"

print "Team", W, E, E, D

favCard = Card.new('Kc')
testBoard1 = [
    Card.new('Ah'),
    Card.new('Kd'),
    Card.new('Jc')
]

testHand1 = [
    Card.new('Qs'),
    Card.new('Th')
]

evaluator = Evaluator()
print evaluator.evaluate(testBoard1, testHand1)
