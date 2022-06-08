import cv2
import numpy as np
import time
import os
from copy import deepcopy
import random
import pygame
from PIL import Image
import Cards
import VideoStream
import Algorithm


IM_WIDTH = 1280
IM_HEIGHT = 720 

# Initialize camera object and video feed from the camera
videostream = VideoStream.VideoStream((IM_WIDTH,IM_HEIGHT),1).start()
time.sleep(1)

# Load the train move images
path = os.path.dirname(os.path.abspath(__file__))
train_move = Cards.load_moves( path + '/Img/')

ROWS, COLS = 10,10
SQUARE_SIZE = 50
HEIGHT, WIDTH = ROWS*SQUARE_SIZE, COLS*SQUARE_SIZE 

WIN = pygame.display.set_mode((WIDTH*2, HEIGHT))
board=Algorithm.Board(ROWS,COLS,SQUARE_SIZE,WIN,HEIGHT,WIDTH)

history,deck = Algorithm.create_deck(WIN,WIDTH,HEIGHT,SQUARE_SIZE)

# Begin capturing frames
while True:
    image = videostream.read()

    pre_proc = Cards.preprocess_image(image)

    cnts_sort, cnt_is_card = Cards.find_cards(pre_proc)

    if len(cnts_sort) != 0:
        cards = []
        k = 0

        for i in range(len(cnts_sort)):
            if (cnt_is_card[i] == 1):

                cards.append(Cards.preprocess_card(cnts_sort[i],image))
                cards[k].best_move_match,cards[k].move_diff = Cards.match_card(cards[k],train_move)
                image, name = Cards.draw_results(image, cards[k])
                k = k + 1

                if len(history.keys())==0:
                    history[name] = 1
                elif name in history.keys():
                    # after 100 consecutive choices of the same move
                    if history[name]==100:
                        num = int(name[5::])
                        if num<3:
                            # Moves 1 and 2 are the starting ones
                            board.start(num,WIN)
                        else:
                            deck = Algorithm.update_deck(deck,num,board,WIN,SQUARE_SIZE,HEIGHT,ROWS,COLS)
                            history={}
                    else:
                        history[name]+=1
                else:
                    history={name:1}

        if (len(cards) != 0):
            temp_cnts = []
            for i in range(len(cards)):
                temp_cnts.append(cards[i].contour)
            cv2.drawContours(image,temp_cnts, -1, (255,0,0), 2)

    else:
        history={}

    # Display the image with the identified cards
    pygame_image = Algorithm.cvimage_to_pygame(image)
    WIN.blit(pygame.transform.scale(pygame_image, (WIDTH,IM_HEIGHT/IM_WIDTH*HEIGHT)), (WIDTH,0))
    pygame.display.update()

    # Define quit button
    event = pygame.event.wait(1)
    if event.type == pygame.QUIT:
        pygame.quit()
        videostream.stop()
