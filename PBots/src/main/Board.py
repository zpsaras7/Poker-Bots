from deuces import Deck
from deuces import Card

class Board:
    board_cards = []
    my_hand = None
    deck = Deck()
    
    #Both player hand and flop cards should be in the 
    # form of strings
    def __init__(self, new_deck, player_hand_string, flop=False):
        self.my_hand = [Card.new(i) for i in player_hand_string]
        self.deck = new_deck
        self.deck.cards.remove(self.my_hand[0])
        self.deck.cards.remove(self.my_hand[1])
        if flop:
            for new_card in flop:
                self.board_cards.append(Card.new(new_card))
                self.deck.cards.remove(self.board_cards[-1])
        
    #Input is a user Specified string
    def add(self, new_card):
        nc = Card.new(new_card)
        if nc in self.deck.cards:
            self.board_cards.append(nc)
            self.deck.cards.remove(self.board_cards[-1])
        else:
            raise Exception("Found repeated card: "+str(new_card))
        
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
          

