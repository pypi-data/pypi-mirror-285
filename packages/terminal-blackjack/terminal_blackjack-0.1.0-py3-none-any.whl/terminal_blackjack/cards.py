import random

class Card:
    def __init__ (self, suit, face, value):
        self.suit = suit
        self.face = face
        self.value = value

    def set_value (self, value):
        self.value = value

    def __str__(self) -> str:
        return f'{self.face} of {self.suit}'
    
    def __repr__(self) -> str:
        return self.__str__()

def initialize(list):
    suits = ['spades', 'clubs', 'diamonds', 'hearts']
    faces = ['king', 'queen', 'jack', 'ace']

    for suit in suits:
        for value in range (1,10):
            list.append(Card(suit, value, value))
        for face in faces[:3]:
            list.append(Card(suit, face, 10))
        list.append(Card(suit, faces[3], 11))

def hit(source_list, target_list):
    random_card = random.choice(source_list)
    if value(target_list) > 21:
        for card in target_list:
            if card.value == 11:
                card.set_value(1)
    target_list.append(random_card)
    source_list.remove(random_card)

def value(source_list):
    value = 0
    for card in source_list:
        value += card.value
    return value