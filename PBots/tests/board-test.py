import Board

from deuces import Deck
from deuces import Evaluator
from deuces import Card

evalutor = Evaluator()
deck = Deck()
p1 = ['Th','9d']
c = ['6c', '7d','2c']

b = Board.Board(deck, p1, c)
print evalutor.evaluate(b.my_hand, b.board_cards)
b.printBoard()
# b.addRandomly()
# print evalutor.evaluate(b.my_hand, b.board_cards)
# b.printBoard()
# b.add('As')
# print evalutor.evaluate(b.my_hand, b.board_cards)
# b.printBoard()
b.fillBoardRandomly()
print evalutor.evaluate(b.my_hand, b.board_cards)
b.printBoard()