import random
from pymongo import MongoClient as mc
import os
from dotenv import load_dotenv


local_uri = os.getenv('MONGODB_LOCAL_URI')
jollieb = os.getenv('JOLLIEB')
client = mc(local_uri)
db = client.mulligan
coll = db.decks

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
    def __init__(self, cards: list, stats: list):
        self.life = []
        self.hand = []
        self.trash = []
        self.field = []
        if len(cards) == 50: #50
            self.cards = cards
            self.stats = stats
        else:
            raise ValueError("The deck must contain exactly 50 cards.")
        
        
    def check(self):
        return [self.hand, self.life, self.cards]

    def shuffle(self, option: bool = False):
        random.shuffle(self.cards)
        if option is True:
            return self.hand
    
    def draw_five(self, option: bool = False):
        self.hand = self.cards[:5]
        if option is True:
            self.cards = self.cards[5:]
            return self.hand
        else:
            return self.hand

    def add_life(self, number: int):
        self.life = self.cards[:number]
        self.cards = self.cards[number:]
        return [self.life, self.cards]

    def draw(self):
        self.hand.append(self.cards[0])
        self.cards = self.cards[1:]
        return [self.hand, self.cards]

    def take_life(self):
        self.hand.append(self.life[0])
        self.life = self.life[1:]
        return [self.hand, self.life]
    
    def play(self, amount: int): #what if this is a discord select?
        self.field = self.hand[:amount]
        self.hand = self.hand[amount:]
        return self.hand

    def ko(self, amount: int): #what if this is a discord select?
        self.trash = self.field[:amount]
        self.field = self.field[amount:]
        return self.field

    def play_from_trash(self, amount: int): #what if this is a discord select?
        self.field = self.trash[:amount]
        self.trash = self.trash[amount:]

    def counter(self, amount: int): #what if this is a discord select?
        self.hand = self.hand[amount:]
        return self.hand

    def trigger(self): #If condition. Assumes all trigger effects go to play or trash, if your trigger effect may state draw, add_life, or remove from trash. use other functions accordingly.
        self.trash = self.life[0]
        self.life = self.life[1:]
        return self.life
    
    def trash_deck(self, amount: int): 
        self.cards = self.cards[amount:]
        return self.cards

    def checkstats(self): #should be displayed in an embed already
        visible_cards = self.field + self.trash + self.hand
        pass

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
        self.E6 = {"type":"event","counter":6000,"trigger":False}
        self.E10 = {"type":"event","counter":10000,"trigger":False} #P-059 Uta Counter Event card.
        self.ET = {"type":"event","counter":0,"trigger":True}
        self.E1T = {"type":"event","counter":1000,"trigger":True}
        self.E2T = {"type":"event","counter":2000,"trigger":True}
        self.E3T = {"type":"event","counter":3000,"trigger":True}
        self.E4T = {"type":"event","counter":4000,"trigger":True}
        self.E5T = {"type":"event","counter":5000,"trigger":True} 
        self.E6T = {"type":"event","counter":6000,"trigger":True}
        self.ST = {"type":"stage","counter":0,"trigger":True}
        self.S = {"type":"stage","counter":0,"trigger":False}

# doc = coll.find_one({"uid":str(jollieb)},{"_id":0})
# deck = doc["deck"]
# stats = doc["stats"]
# 
# sim = Deck(cards=deck,stats=stats)
# 
# # After pressing "Start"
# sim.shuffle()
# hand = sim.draw_five()
# print(f"1st hand: {hand}")
# 
# # If user presses mulligan
# sim.shuffle()
# hand = sim.draw_five()
# print(f"2nd hand: {hand}")
# 
# # If not:
# hand = sim.draw_five(True)
# 
# # After Mulligan
# sim.add_life(4) #Zoro Sanji
# print(f"Life: {sim.life}")
# 
# ## Buttons (Attacking Turn):
# #sim.draw()
# #sim.play()
# #sim.take_life()
# #sim.add_life()
# #sim.play_from_trash()
# #sim.trash_deck()
# #
# ## Buttons (Defending Turn):
# #sim.counter()
# #sim.take_life() # Might have trigger, when it does sim.trigger()
# 
# print(f"Final hand: {hand}")

