import random

# A deck can contain the ff:
# event, character, stage (E,C,S)

# Then a character card can have one or more traits including:
# 1k counter, 2k counter, trigger (12T)

# For events, and stages, it can be characterized as:
# 2k counter, trigger

# "Trigger" keyword:
# Card with this keyword will not be added to hand, unless stated otherwise.
# Its effect can also remove one or more cards from hand.

class Deck:
    def __init__(self, cards: list):
        self.life = None
        self.hand = None
        if len(cards) < 50: #50
            self.cards = cards
        else:
            raise ValueError("The deck must contain exactly 50 cards.")

    def shuffle(self):
        random.shuffle(self.cards)
    
    def draw_five(self, option: bool = False):
        self.hand = self.cards[:5]
        if option is True:
            self.cards = self.cards[5:]
        return self.hand

    def add_life(self, number):
        self.life = self.cards[:number]
        self.cards = self.cards[number:]

    def draw(self):
        self.hand.append(self.cards[0])
        self.cards = self.cards[1:]
        return self.hand, self.cards 

    def take_life(self):
        self.hand.append(self.life[0])
        self.life = self.life[1:]
        return self.hand, self.life
    
    def trash(self, option, amount=None):
        if option == "trigger":
            self.life = self.life[1:]
        if option == "counter":
            self.hand = self.hand[amount:]
        if option == "deck":
            self.cards = self.cards[amount:]

class Card:
    def __init__(self):
        self.C1T = {"type":"character","counter":1000,"trigger":True}
        self.C2T = {"type":"character","counter":2000,"trigger":True}
        self.CT = {"type":"character","counter":0,"trigger":True}
        self.C1 = {"type":"character","counter":1000,"trigger":False}
        self.C2 = {"type":"character","counter":2000,"trigger":False}
        self.C = {"type":"character","counter":0,"trigger":False}
        self.E = {"type":"event","counter":0,"trigger":False}
        self.E1 = {"type":"event","counter":1000,"trigger":False}
        self.E2 = {"type":"event","counter":2000,"trigger":False}
        self.E3 = {"type":"event","counter":3000,"trigger":False}
        self.E4 = {"type":"event","counter":4000,"trigger":False}
        self.E5 = {"type":"event","counter":5000,"trigger":False} #No cards with this trait exist to this day.
        self.E6 = {"type":"event","counter":6000,"trigger":False}
        self.ET = {"type":"event","counter":0,"trigger":True}
        self.E1T = {"type":"event","counter":1000,"trigger":True}
        self.E2T = {"type":"event","counter":2000,"trigger":True}
        self.E3T = {"type":"event","counter":3000,"trigger":True}
        self.E4T = {"type":"event","counter":4000,"trigger":True}
        self.E5T = {"type":"event","counter":5000,"trigger":True}
        self.E6T = {"type":"event","counter":6000,"trigger":True}
        self.ST = {"type":"stage","counter":0,"trigger":True}
        self.S = {"type":"stage","counter":0,"trigger":False}
    
# my_deck = Deck([1,2,3,4,5,6,7,8,9,10])
# my_deck.shuffle()
# print(my_deck.draw_five(True))
# my_deck.add_life(2)
# print(my_deck.take_life())

# card = Card()
# 
# decklist = []
# 
# 
# 
# counters = [item["counter"] for item in deck.cards]
# print(counters)