from deuces import *


class Board:
    
    #Both player hand and flop cards should be in the 
    # form of strings
    def __init__(self, player_hand, flop=False):
        self.deck = Deck()
        self.my_hand = player_hand
        self.board_cards = []
        self.deck.cards.remove(self.my_hand[0])
        self.deck.cards.remove(self.my_hand[1])
        if flop:
            for new_card in flop:
                self.board_cards.append(new_card)
    
    def emptyBoardRandomRank(self):
        assert len(self.board_cards)==0
        self.addRandomly(3)
        ev = Evaluator()
        return ev.evaluate(self.my_hand, self.board_cards)
        
    #Input is how many random cards we want to draw from existing deck
    def addRandomly(self, n=1):
        nc = self.deck.draw(n)
        if n==1:
            self.board_cards.append(nc)
        else:
            self.board_cards.extend(nc)
        
    
    def fillBoardRandomly(self):
        left_to_draw = 5-len(self.board_cards)
        self.addRandomly(left_to_draw)
          
    def printBoard(self):
        print "My Hand:  "
        Card.print_pretty_cards(self.my_hand)
        print "Board:  "
        Card.print_pretty_cards(self.board_cards)
          

