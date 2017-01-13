from deuces import Card
from deuces import Evaluator
import matplotlib.pyplot as plt

plt.plot([1, 3, 5, 11, 13, 17, 19])
plt.show()

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

