from deuces import Deck
from deuces import Card

class Board:
    board_cards = []
    my_hand = None
    deck = Deck()
    
    #Both player hand and flop cards should be in the 
    # form of strings
    def __init__(self, player_hand_string, flop=False):
        self.my_hand = [Card.new(i) for i in player_hand_string]
        
        self.deck.cards.remove(self.my_hand[0])
        self.deck.cards.remove(self.my_hand[1])
        print len(self.deck.cards)
        if flop:
            for new_card in flop:
                self.board_cards.append(Card.new(new_card))
                self.deck.cards.remove(self.board_cards[-1])
        
        print self.my_hand
        print self.board_cards
        print len(self.deck.cards)
        
    def add(self, new_card):
        self.board_cards.append(Card.new(new_card))
        self.deck.cards.remove(self.board_cards[-1])
    
    def fillBoardRandomly(self):
        while len(self.board_cards) != 5:
            self.board_cards.append(self.deck.draw())
            #Make sure that drawing from deck removes cards from the deck
          
    def printBoard(self):
        print "My Hand:  "
        Card.print_pretty_cards(self.my_hand)
        print "Board:  "
        Card.print_pretty_cards(self.board_cards)
          

