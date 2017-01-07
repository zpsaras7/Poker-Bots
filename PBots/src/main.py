import Board

from deuces import Deck
from deuces import Evaluator
from deuces import Card

evalutor = Evaluator()
deck = Deck()
p1 = ['Th','9d']
c = ['6c', '7d','2c']

b = Board.Board(p1, c)
print evalutor.evaluate(b.my_hand, b.board_cards)
b.printBoard()
b.add(Card.int_to_str(deck.draw()))
print evalutor.evaluate(b.my_hand, b.board_cards)
b.printBoard()