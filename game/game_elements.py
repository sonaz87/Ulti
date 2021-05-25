# -*- coding: utf-8 -*-
"""
Created on Mon May 17 14:25:07 2021

@author: lor
"""

from random import shuffle
from random import choices
import pygame
import pika
import sys
import json
import jsonpickle
from pygame.locals import *


SZINES = 'szines'
SZINTELEN = 'szintelen'


class Player(object):
    def __init__(self, name):
        self.name = name
        self.is_dealer = False
        self.is_active = False
        self.hand = []
        self.discard = []
        self.sorting = SZINES
        self.points = 0
    
    def get_name(self):
        return self.name
    
    def set_dealer(self, val):
        self.is_dealer = val
        
    def get_dealer(self):
        return self.is_dealer
    
    def set_active(self, val):
        self.is_active = val
        
    def get_active(self):
        return self.is_active
    
    def set_hand(self, cards):
        self.hand = cards[:]
        
    def play_card(self, card):
        x = self.hand.pop(card)
        return x
    
    def to_discard(self, cards):
        self.discard.extend(cards)
        
    def get_discard(self):
        return self.discard

    def sort_hand(self):
        COLOR_NUMBER = dict()
        VALUE_NUMBER = dict()
        
        if self.sorting == SZINES:
            VALUES = ["hetes", "nyolcas", "kilences", "also", "felso", "kiraly", "tizes", "asz"]
        elif self.sorting == SZINTELEN:
            VALUES = ["hetes", "nyolcas", "kilences", "tizes", "also", "felso", "kiraly", "asz"]
        
        COLORS = ['zold', 'makk', 'tok', 'piros']            
        
        for i in range(len(COLORS)):
            COLOR_NUMBER.update({COLORS[i] : i})
        for i in range(len(VALUES)):
            VALUE_NUMBER.update({VALUES[i] : i})
            
        self.hand.sort(key = lambda x: (COLOR_NUMBER[x.color], VALUE_NUMBER[x.value]))
        
    def update_points(num):
        self.points += num

        
        
class Card(object):
    def __init__(self, color, value, name):
        self.color = color
        self.value = value
        self.img = None
        self.name = name
        
    def __repr__(self):
        return self.name
        
    def set_img(self, image):
        self.img = image
    
    def get_value(self):
        return self.value
    
    def get_color(self):
        return self.color
    
    
    def get_img(self):
        return self.img

class Message(object):
    def __init__(self, message_type, player, body):
        self.message_type = message_type
        self.player = player
        self.body = body
        
    def __str__(self):
        return self.message_type + " " + self.body

    

class Popup(object):
    def __init__(self, player, message):
        self.player = player
        self.message = message
        
    def get_player(self):
        return self.player
    
    def get_message(self):
        return self.message
    
    def __len__(self):
        return len(self.message)

    
    


class Deck(object):

    def __init__(self):
        VALUES = ["hetes", "nyolcas", "kilences", "tizes", "also", "felso", "kiraly", "asz"]
        COLORS = ['zold', 'makk', 'tok', 'piros']
        NAME_VALUES = ["hetes", "nyolcas", "kilences", "tízes", "alsó", "felső", "király", "ász"]
        NAME_COLORS = ['Zöld', 'Makk', 'Tök', 'Piros']
        self.cards = []
        for i in range(len(COLORS)):
            for j in range(len(VALUES)):
                self.cards.append(Card(COLORS[i], VALUES[j], NAME_COLORS[i] + " " + NAME_VALUES[j]))
                
    def shuffle(self):
        shuffle(self.cards)
        
    def deal(self, player, start_number, stop_number):
        hand = self.cards[start_number, stop_number]
        return (player, hand)
        


class Alapjatek(object):
    def __init__(self):
        self.vallalo = None
        
class Szines(Alapjatek):
    def __init__(self):
        super().__init__()
        self.number_values = ["hetes", "nyolcas", "kilences", "also", "felso", "kiraly", "tizes", "asz"]
        self.adu = None
        
    def set_adu(self, adu):
        self.adu = adu
    
class Szintelen(Alapjatek):       
    def __init__(self):
        super().__init__()
        self.number_values = ["hetes", "nyolcas", "kilences", "tizes", "also", "felso", "kiraly", "asz"]



class Passz(Szines):
    pass
class PirosPassz(Szines):
    pass
class NegyvenSzaz(Szines):
    pass
class Ulti(Szines):
    pass
class Betli(Szintelen):
    pass
class Durchmarsch(Szines):
    pass

class SzintelenDurchmarsch(Szintelen):
    pass

class NegyvenSzazUlti(Szines):
    pass
class PirosNegyvenSzaz(Szines):
    pass
class HuszSzaz(Szines):
    pass
class PirosUlti(Szines):
    pass
class NegyvenSzazDurchmarsch(Szines):
    pass
class UltiDurchmarsch(Szines):
    pass
class Rebetli(Szintelen):
    pass
class HuszSzazUlti(Szines):
    pass
class ReDurchmarsch(Szintelen):
    pass
class PirosDurschmarsch(Szines):
    pass
class NegyvenSzazUltiDurchmarsch(Szines):
    pass
class HuszSzazDurchmarsch(Szines):
    pass
class PirosNegyvenSzazUlti(Szines):
    pass
class PirosHuszSzaz(Szines):
    pass
class HuszSzazUltiDurchmarsch(Szines):
    pass
class PirosNegyvenSzazDurchmarsch(Szines):
    pass
class PirosUltiDurchmarsch(Szines):
    pass
class TeritettBetli(Szintelen):
    pass
class PirosHuszSzazUlti(Szines):
    pass
class TeritettDurchmarsch(Szines):
    pass
class SzintelenTeritettDurchmarsch(Szintelen):
    pass
class PirosNegyvenSzazUltiDurchmarsch(Szines):
    pass
class PirosHuszSzazDurchmarsch(Szines):
    pass
class TeritettNegyvenSzazDurchmarsch(Szines):
    pass
class TeritettUltiDurchMarsch(Szines):
    pass
class TeritettNegyvenSzazUltiDurchmarsch(Szines):
    pass
class TeritettPirosNegyvenSzazDurchmarsch(Szines):
    pass
class PirosTeritettNegyvenSzazUltiDurchmarsch(Szines):
    pass
class TeritettHuszSzazDurchmarsch(Szines):
    pass
class PirosUltiDurchmarschHuszSzaz(Szines):
    pass
class TeritettUltiDurchmarschHuszSzaz(Szines):
    pass
class PirosTeritettNegyvenSzazUltiDurchmarsch(Szines):
    pass
class PirosTeritettDurchmarschHuszSzaz(Szines):
    pass
class PirosTeritettUltiDurchmarschHuszSzaz(Szines):
    pass
