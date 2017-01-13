from deuces import *

W = "Pt"
E = "mc^2"
D = "(b^2-4ac)"
print "Team", W, E, E, D

handStrength_strongest = 1
handStrength_weakest = 7462 #per deuces readme

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
