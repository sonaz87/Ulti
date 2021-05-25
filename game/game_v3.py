# -*- coding: utf-8 -*-
"""
Created on Mon May 17 07:39:59 2021

@author: lor
"""

# __all__ = ['main']

import pygame
import pygame_menu
import urllib.request
from pygame_menu.examples import create_example_window
import threading
import pika
import sys
import time
import json
import jsonpickle
import random
from game_elements import *

from random import randrange
from typing import Tuple, Any, Optional, List


POPUP = 'popup'
JOIN = 'join'
DEAL_HAND = 'deal_hand'
BID = 'bid'
PLAY_CARD = 'play_card'
INIT = 'init'
SHOW_DSCARD = 'show_discard'
SHOW_TALON = 'show_talon'
BIDDING = 'Bidding'
GAME_PHASE = 'game_phase'


def send_server_message(message):

    
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    
    channel.exchange_declare(exchange='server_comm', exchange_type='fanout')
    
    # message = ' '.join(sys.argv[1:]) or "info: Hello World!"
    channel.basic_publish(exchange='server_comm', routing_key='', body=message, mandatory=True)
    print(" [x] Servers ent %r" % jsonpickle.decode(message))
    connection.close()

def send_client_message(message):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='client_comm')
    channel.basic_publish(exchange='', routing_key='client_comm', body=message, mandatory=True)
    print("client message sent")
    connection.close()
    

def server_listener():
    global players
    global popup
    
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost')
        )
    channel = connection.channel()
    channel.queue_declare(queue='client_comm')
    
    def callback(ch, method, properties, body):
        print(" [x] server received message %r" % jsonpickle.decode(body))
        if jsonpickle.decode(body).message_type == POPUP:
            send_server_message(body)

        if jsonpickle.decode(body).message_type == JOIN:
            if jsonpickle.decode(body).player not in players:
                players.append(jsonpickle.decode(body).player)
                print("players: ", players)

        
    channel.basic_consume(
        queue='client_comm', on_message_callback=callback, auto_ack=True)    
    print(" * Server waiting for messages...")

    channel.start_consuming()

def client_listener():
    global message

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    
    channel.exchange_declare(exchange='server_comm', exchange_type='fanout')
    
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    
    channel.queue_bind(exchange='server_comm', queue=queue_name)
    
    print(' [*] Client waiting for messages. To exit press CTRL+C')
    
    def callback(ch, method, properties, body):
        
        print(" [x] client received message:  %r" % jsonpickle.decode(body))
        message.append(jsonpickle.decode(body))

    
    channel.basic_consume(
        queue=queue_name, on_message_callback=callback, auto_ack=True)
    
    channel.start_consuming() 


def game_gui(player_in):
    global message

    card_images = dict()
    deck = Deck()
    game_phase = INIT
    current_game_value = 0
    
    possible_games = {
        'Passz' : [1, Passz()],
        'Piros passz' : [2, PirosPassz()],
        'Negyven-száz' : [3, NegyvenSzaz()],
        'Ulti' : [4, Ulti()],
        'Betli' : [5, Betli()],
        'Durchmarsch' : [6, Durchmarsch()],
        'Színtelen durchmarsch' : [6, SzintelenDurchmarsch()],
        'Negyven-száz Ulti' : [7, NegyvenSzazUlti()],
        'Piros negyven-száz' : [8, PirosNegyvenSzaz()],
        'Húsz-száz' : [9, HuszSzaz()],
        'Piros ulti' : [10, PirosUlti()],
        'Negyven-száz durchmarsch' : [11, NegyvenSzazDurchmarsch()],
        'Ulti durchmarsch' : [11, UltiDurchmarsch()],
        'Rebetli' : [12, Rebetli()],
        'Húsz-száz ulti' : [13, HuszSzazUlti()],
        'Redurchmarsch' : [14, ReDurchmarsch()],
        'Piros durchmarsch' : [14, PirosDurschmarsch()],
        'Negyven-száz ulti durschmarsch' : [15, NegyvenSzazUltiDurchmarsch()],
        'Húsz-száz durchmarsch' : [16, HuszSzazDurchmarsch()],
        'Piros negyven-száz ulti' : [17, PirosNegyvenSzazUlti()],
        'Piros húsz-száz' : [18, PirosHuszSzaz()],
        'Húsz-száz ulti durchmarsch' : [19, HuszSzazUltiDurchmarsch()],
        'Piros negyven-száz durchmarsch' : [20, PirosNegyvenSzazDurchmarsch()],
        'Piros ulti durchmarsch' : [20, PirosUltiDurchmarsch()],
        'Terített betli' : [21, TeritettBetli()],
        'Piros húsz-száz ulti' : [22, PirosHuszSzazUlti()],
        'Terített durchmarsch' : [23, TeritettDurchmarsch()],
        'Színtelen terített durchmarsch' : [23, SzintelenTeritettDurchmarsch()],
        'Piros negyven-száz ulti durchmarsch' : [24, PirosNegyvenSzazUltiDurchmarsch()],
        'Piros húsz-száz durchmarsch' : [25, PirosHuszSzazDurchmarsch()],
        'Terített negyven-száz durchmarsch' : [26, TeritettNegyvenSzazDurchmarsch()],
        'Terített ulti durchmarsch' : [26, TeritettUltiDurchMarsch()],
        'Terített negyven-száz ulti durchmarsch' : [27, TeritettNegyvenSzazUltiDurchmarsch()],
        'Terített piros negyven-száz durchmarsch' : [28, TeritettPirosNegyvenSzazDurchmarsch()],
        'Terített piros ulti durchmarsch' : [28, PirosTeritettNegyvenSzazUltiDurchmarsch()],
        'Terített húsz-száz durchmarsch' : [28, TeritettHuszSzazDurchmarsch()],
        'Piros ulti durchmarsch húsz-száz' : [29, PirosUltiDurchmarschHuszSzaz()],
        'Terített ulti durchmarsch húsz-száz' : [29, TeritettUltiDurchmarschHuszSzaz()],
        'Piros terített negyven-száz ulti durchmarsch' : [30, PirosTeritettNegyvenSzazUltiDurchmarsch()],
        'Piros terített durchmarsch húsz-száz' : [31, PirosTeritettDurchmarschHuszSzaz()],
        'Piris terített ulti durchmarsch húsz-száz' : [32, PirosTeritettUltiDurchmarschHuszSzaz()]
        }
    
    for card in deck.cards:
        card_images.update({card.color + card.value : pygame.image.load('D:/python projects/ulti/GUI/images/' + card.color + card.value + '.jpg')})

    
    player = player_in
    
    pygame.init()
    DISPLAYSURF = pygame.display.set_mode((1400, 900), 0, 32)
    pygame.display.set_caption('Ulti')
    table_img = pygame.image.load(r'D:/python projects/ulti/GUI/images/table.jpg')

    BLACK = (  0,   0,   0)
    WHITE = (255, 255, 255)
    RED = (255,   0,   0)
    GREEN = (  0, 255,   0)
    BLUE = (  0,   0, 255)
    GREY = (150 , 150, 150)
    LIGHT_GREY = (200, 200, 200)
    popup_text = 'Test'
    popup_msg = ''
    fontObj = pygame.font.Font('C:/Windows/Fonts/Calibri.ttf', 32)
    fontObj2 = pygame.font.Font('C:/Windows/Fonts/Calibri.ttf', 12)
    fontObj3 = pygame.font.Font('C:/Windows/Fonts/Calibri.ttf', 18)
    fontObj3.bold
    textSurfaceObj = fontObj.render(popup_text, True, WHITE)
    textRectObj = textSurfaceObj.get_rect() 
    textRectObj.center = (200, 150)
    
    # popup messages
    popupSurf1 = fontObj2.render('Placeholder1', True, WHITE)
    popupSurf2 = fontObj2.render('Placeholder2', True, WHITE)
    popupSurf3 = fontObj2.render('Placeholder3', True, WHITE)
    popupSurf4 = fontObj2.render('Placeholder4', True, WHITE)
    popupSurf5 = fontObj2.render('Placeholder5', True, WHITE)
    popupRectObj1 = popupSurf1.get_rect()
    popupRectObj2 = popupSurf1.get_rect()
    popupRectObj3 = popupSurf1.get_rect()
    popupRectObj4 = popupSurf1.get_rect()
    popupRectObj5 = popupSurf1.get_rect()
    popupRectObj1.center = (1300, 400)
    popupRectObj2.center = (1300, 420)
    popupRectObj3.center = (1300, 440)
    popupRectObj4.center = (1300, 460)
    popupRectObj5.center = (1300, 480)
    

    # name tags
    p2NameSurf = fontObj.render('Várakozás a többiekre', True, WHITE)
    p3NameSurf = fontObj.render('Várakozás a többiekre', True, WHITE)
    
    p2NameRect = p2NameSurf.get_rect()
    p3NameRect = p3NameSurf.get_rect()
    
    p2NameRect.top = (34)
    p2NameRect.left = (50)
    p3NameRect.top = (34)
    p3NameRect.right = (1350)
    
    

    
    while True:
        
        # message handling:
        
        selected_cards = []    
        
        try:
            if len(message) > 0:
                print(message[0].message_type, " received")
                if message[0].message_type == POPUP:
                    print("popup found")
                    popupSurf1, popupSurf2, popupSurf3, popupSurf4 = popupSurf2, popupSurf3, popupSurf4, popupSurf5
                    popupSurf5 = fontObj2.render(message[0].player.name + ": " + message[0].body, True, WHITE)
                elif message[0].message_type == INIT:
                    msg = message[0].body
                    print("init arrived")
                    if msg[0].name == player.name:
                        p2NameSurf = fontObj.render(msg[1].name + " - " + str(msg[1].points), True, WHITE)
                        p3NameSurf = fontObj.render(msg[2].name + " - " + str(msg[2].points), True, WHITE)
                    elif msg[1].name == player.name:
                        p2NameSurf = fontObj.render(msg[2].name + " - " + str(msg[2].points), True, WHITE)
                        p3NameSurf = fontObj.render(msg[0].name + " - " + str(msg[0].points), True, WHITE)
                    elif msg[2].name == player.name:
                        p2NameSurf = fontObj.render(msg[0].name + " - " + str(msg[0].points), True, WHITE)
                        p3NameSurf = fontObj.render(msg[1].name + " - " + str(msg[1].points), True, WHITE)                        
                elif message[0].message_type == DEAL_HAND:
                    print("deal_hand received")
                    for pl in message[0].body:
                        if pl.name == player.name:
                            player = pl
                elif message[0].message_type == GAME_PHASE:
                    print("game phase message received")
                    game_phase = message[0].body
                message.pop()



        except:
            raise
        DISPLAYSURF.blit(table_img, (0, 0))        
        
        button = pygame.draw.rect(DISPLAYSURF, RED, (150, 100, 100, 100))
        
        sortSurf = fontObj3.render('Rendezés színtelenre' if player.sorting == SZINES else "Rendezés színesre", True, BLACK)
        sortRect = sortSurf.get_rect()
        sortRect.left = 30
        sortRect.bottom = 600
        
        DISPLAYSURF.blit(textSurfaceObj, textRectObj)
        DISPLAYSURF.blit(popupSurf1, popupRectObj1)
        DISPLAYSURF.blit(popupSurf2, popupRectObj2)
        DISPLAYSURF.blit(popupSurf3, popupRectObj3)
        DISPLAYSURF.blit(popupSurf4, popupRectObj4)
        DISPLAYSURF.blit(popupSurf5, popupRectObj5)
        DISPLAYSURF.blit(p2NameSurf, p2NameRect)
        DISPLAYSURF.blit(p3NameSurf, p3NameRect)
        cards_to_display = []
        if len(player.hand) > 0:
            player.sort_hand()
            for card in player.hand:
                card_display = []
                cardSurf = card_images[card.color+card.value]
                cardRect = cardSurf.get_rect()
                cards_to_display.append([cardSurf, cardRect])
        if len(cards_to_display) > 0:
            displacement = 50
            for i in cards_to_display:    
                if i in selected_cards:
                    i[1].bottom = 840
                else:
                    i[1].bottom = 890
                i[1].left = displacement
                DISPLAYSURF.blit(i[0], i[1])
                displacement += 80
            sortButton = pygame.draw.rect(DISPLAYSURF, GREY, sortRect)
            DISPLAYSURF.blit(sortSurf, sortRect)
                
        if game_phase == BIDDING and player.is_active:
            #TODO!
            # választható játékokat felkínálni
            licit_items = []
            licit_selected = None
            licit_displacement = 20
            for key in possible_games.keys():
                if possible_games[key][0] > current_game_value:
                    licitSurf = fontObj.render(key, True, RED if key == licit_selected else BLACK)
                    licitRect = licitSurf.get_rect()
                    licit_items.append([licitSurf, licitRect])
                    
            licit_box = pygame.draw.rect(DISPLAYSURF, LIGHT_GREY, (400, 10, 600, 15*len(licit_items) + 100))
            for element in licit_items:
                element[1].centerx = 700
                element[1].top = licit_displacement
                DISPLAYSURF.blit(element[0], element[1])
                licit_displacement += 18
            
            
            
            # kártyák kiválasztása gombot megcsinálni
            # csak akkor legyen aktív, ha pontosan két kártya van kiválasztva
            # gomb megnyomására a két kártyát kiveszem a kézből, beteszem a talonba
            # talon-t elküldöm a szervernek
            # szerver átállítja az aktív játékost
            # aktív játékos felveheti a talont
            # ha a game_phase BIDDING és én vagyok az aktív és csak tíz lapom van:
                # megcsinálni a felveszem és passz gombokat
                # felvétel után a talon megy a kézbe és a selectedbe
                
            
            
            pass
            
        mouseClicked = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mouseClicked = True
            if mouseClicked and button.collidepoint(mousex, mousey):
                msg = jsonpickle.encode(Message('popup', player, 'Test'), unpicklable = True)
                send_client_message(msg)
            try:    
                if mouseClicked and sortButton.collidepoint(mousex, mousey):
                    if player.sorting == SZINES:
                        player.sorting = SZINTELEN
                    elif player.sorting == SZINTELEN:
                        player.sorting = SZINES
                    player.sort_hand()
            except:
                pass
            
            try:
                if player.is_active:                        
                    for i in range(len(cards_to_display)):
                        if mouseClicked and cards_to_display[i].collidepoint(mousex, mousey):
                            if cards_to_display[i] in selected_cards:
                                selected.pop(cards_to_display[i])
                            else:
                                if game_state == BIDDING:
                                    if len(selected_cards) < 2:
                                        selected_cards.append(cards_to_display[i])
                                    if len(selected_cards) == 2:
                                        selected_cards.pop(0)
                                        selected_cards.append(cards_to_display[i])
            except:
                pass                
        pygame.display.update()


    
    
def main(test: bool = False):


    # -------------------------------------------------------------------------
    # Globals
    # -------------------------------------------------------------------------
    global main_menu
    global surface
    # global name
    # global ip

    def play_join():
        global player
        global message
        message = []
        p_name = join_name.get_value()
        if p_name == '':
            p_name = host_name.get_value()
        h_ip = ip.get_value()
        if h_ip == '':
            h_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')

        print("game started")
        print("name :", p_name)
        print('ip: ', h_ip)
        
        
        # def msg_tester():
        #     # global message
        #     while True:
        #         if len(message) > 0:
        #             print("message tester")
        #             print(message)
        #             break
        
        player = Player(p_name)
        

        
        listener_thread = threading.Thread(target = client_listener)
        listener_thread.setDaemon(True)
        listener_thread.start()        
        
        # test = threading.Thread(target = msg_tester)
        # test.setDaemon(True)
        # test.start()
        
        game_thread = threading.Thread(target = game_gui(player))
        game_thread.setDaemon(True)
        game_thread.start()
    
        join_msg = jsonpickle.encode(Message(JOIN, player, ''), unpicklable = True)
        while message[0].message_type != INIT:
            
            send_client_message(join_msg)        

        
    def play_host():
        global server_started
        
        server_thread = threading.Thread(target = server)
        server_thread.setDaemon(True)
        server_thread.start()
        
        # while True:
        #     if server_started:
        play_join()
        # play_thread = threading.Thread(target = play_join)
        # play_thread.setDaemon(True)
        # play_thread.start()

    def server():



        def wait_for_players():
            global init_done
            global players
            while True:
                if len(players) == 3:
                    print("players: ", players)
                    x = random.choice(players)
                    x.is_dealer = True
                    
                    send_server_message(jsonpickle.encode(Message(POPUP, x , " az osztó"), unpicklable=True))
                    send_server_message(jsonpickle.encode(Message(INIT, 'server', players), unpicklable = True))
                    init_done = True
                    print("init_done in wait for players", init_done)
                    break
                
        def deal_hands(deck):
            global players
            if players[0].is_dealer:
                players[2].set_hand(deck.cards[0:12])
                send_server_message(jsonpickle.encode(Message(POPUP, players[2], " kezd"), unpicklable=True))
                players[2].is_active = True
                players[0].set_hand(deck.cards[12:22])
                players[1].set_hand(deck.cards[22:32])
                
            elif players[1].is_dealer:
                players[0].set_hand(deck.cards[0:12])
                send_server_message(jsonpickle.encode(Message(POPUP, players[0], " kezd"), unpicklable=True))
                players[0].is_active = True
                players[2].set_hand(deck.cards[12:22])
                players[1].set_hand(deck.cards[22:32])
                
            elif players[2].is_dealer:    
                players[1].set_hand(deck.cards[0:12])
                send_server_message(jsonpickle.encode(Message(POPUP, players[1], " kezd"), unpicklable=True))
                players[1].is_active = True
                players[2].set_hand(deck.cards[12:22])
                players[1].set_hand(deck.cards[22:32])
                
            
            
        
        def start_new_game():
            
            game_phase = BIDDING

            
            deck = Deck()
            deck.shuffle()
            deal_hands(deck)
            
            msg = Message(DEAL_HAND, 'server', players)
            send_server_message(jsonpickle.encode(msg, unpicklable=True))
            print("DEAL_HAND sent")

            msg = Message(GAME_PHASE, 'server', game_phase)
            send_server_message(jsonpickle.encode(msg, unpicklable=True))            
        
        
        
        global server_started
        global players
        # global popup
        global game_phase
        global init_done
        init_done = False        
        server_started = False
        print("Starting server")
        
        players = list()
        listener_thread = threading.Thread(target = server_listener)
        listener_thread.setDaemon(True)
        listener_thread.start()        
        print("init_done before wait: ", init_done)
        wait_for_players_thread = threading.Thread(target = wait_for_players)
        wait_for_players_thread.setDaemon(True)
        wait_for_players_thread.start()
        wait_for_players_thread.join()
        
        print("init_done after wait: ", init_done)
        while True:
            if listener_thread.is_alive():
                print("bubu")
                server_started = True
                break
        game_thread = threading.Thread(target = start_new_game)
        game_thread.setDaemon(True)
        if init_done:
            game_thread.start()
        

        
        
        
        
        
    def main_background() -> None:
        """
        Background color of the main menu, on this function user can plot
        images, play sounds, etc.
        :return: None
        """
        surface.fill((40, 40, 40))
        
        
        
    def check_name_test(value: str) -> None:
        """
        This function tests the text input widget.
        :param value: The widget value
        :return: None
        """
        print('User name: {0}'.format(value))
    
    
    def check_IP_test(value: str) -> None:
        """
        This function tests the text input widget.
        :param value: The widget value
        :return: None
        """
        print('IP provided: {0}'.format(value))

   

    # -------------------------------------------------------------------------
    # Create window
    # -------------------------------------------------------------------------
    surface = create_example_window('Example - Multi Input', WINDOW_SIZE)
    clock = pygame.time.Clock()
    
    # -------------------------------------------------------------------------
    # Create menus: Settings
    # ------------------------------------------------------------------------- 
    
    def get_join_data():
        data = join_menu.get_input_data()
        print("join menu data type: ", type(data))
        print("join menu data: ", data)
        return data
    
    def get_host_data():
        data = host_menu.get_data()
        print('host_menu data: ', data)
    

    def get_ip():
        external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
        return external_ip
    
    
    join_menu_theme = pygame_menu.themes.THEME_DEFAULT.copy()
    join_menu_theme.title_offset = (5, -2)
    join_menu_theme.widget_alignment = pygame_menu.locals.ALIGN_LEFT
    join_menu_theme.widget_font = pygame_menu.font.FONT_OPEN_SANS_LIGHT
    join_menu_theme.widget_font_size = 20
    
    join_menu = pygame_menu.Menu(
        height = WINDOW_SIZE[1] * 0.85,
        theme = join_menu_theme,
        title = 'Join',
        width = WINDOW_SIZE[0] * 0.9
        )
    
    join_name = join_menu.add.text_input(
        'Name: ',
        default = '',
        onreturn = check_name_test,
        textinput_id = 'join_name'
        )
    
    ip = join_menu.add.text_input(
        'host IP: ',
        default = '',
        onreturn = check_IP_test,
        textinput_id = 'ip'        
        )
    
    join_menu.add.button(
        'Start',
        play_join
        )
    
    
    join_menu.add.button(
        'Back',
        pygame_menu.events.BACK,
        align = pygame_menu.locals.ALIGN_CENTER
        )



    host_menu_theme = pygame_menu.themes.THEME_DEFAULT.copy()
    host_menu_theme.title_offset = (5, -2)
    host_menu_theme.widget_alignment = pygame_menu.locals.ALIGN_LEFT
    host_menu_theme.widget_font = pygame_menu.font.FONT_OPEN_SANS_LIGHT
    host_menu_theme.widget_font_size = 20   
    
    host_menu = pygame_menu.Menu(
        height = WINDOW_SIZE[1] * 0.85,
        theme = join_menu_theme,
        title = 'Host',
        width = WINDOW_SIZE[0] * 0.9
        )
    
    host_menu.add.text_input(
        'IP',
        default = urllib.request.urlopen('https://ident.me').read().decode('utf8')
        )
    
    host_name = host_menu.add.text_input(
        'Name: ',
        default = '',
        onreturn = check_name_test,
        textinput_id = 'host_name'
        )
    
    host_menu.add.button(
        'Start',
        play_host
        )
    
    host_menu.add.button(
        'Back',
        pygame_menu.events.BACK,
        align = pygame_menu.locals.ALIGN_CENTER
        )    
    


    main_menu_theme = pygame_menu.themes.THEME_DEFAULT.copy()
    main_menu_theme.title_offset = (5, -2)
    main_menu_theme.widget_alignment = pygame_menu.locals.ALIGN_LEFT
    main_menu_theme.widget_font = pygame_menu.font.FONT_OPEN_SANS_LIGHT
    main_menu_theme.widget_font_size = 20      
    
    main_menu = pygame_menu.Menu(
        height=WINDOW_SIZE[1] * 0.7,
        onclose=pygame_menu.events.EXIT,  # User press ESC button
        theme=main_menu_theme,
        title='Main menu',
        width=WINDOW_SIZE[0] * 0.8        
        )
    
    main_menu.add.button(
        'Join',
        join_menu
        )
    
    main_menu.add.button(
        'Host',
        host_menu
        )
    
    main_menu.add.button(
        'Quit',
        pygame_menu.events.EXIT
        )
    
    
    while True:
        clock.tick(FPS)
        main_background()
        main_menu.mainloop(surface, main_background, fps_limit = FPS)
    
        pygame.display.flip()



sound: Optional['pygame_menu.sound.Sound'] = None
surface: Optional['pygame.Surface'] = None
main_menu: Optional['pygame_menu.Menu'] = None


FPS = 60
WINDOW_SIZE = (1400, 900)        
        
if __name__ =='__main__':
    main()
    
    
    
    
    
    