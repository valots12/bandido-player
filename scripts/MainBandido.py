from copy import deepcopy
import random
import pygame
import time
from PIL import Image
import Algorithm

def update(deck,board,WIN,ROWS,COLS):
    # Evaluate each move in every possible direction and choose the one that loads to a minimum number of open roads in the board
    best_deck = {}

    for num in deck:
        original_move=Algorithm.Move(num)

        board.possible_cells()

        possible_moves = []
        prev_x1 = prev_y1 = prev_x2 = prev_y2 = -1

        while True:
            for i in range(ROWS):
                for j in range(COLS):
                    possible_moves,prev_x1,prev_y1,prev_x2,prev_y2 = board.check_up(original_move,possible_moves,i,j,WIN,prev_x1,prev_y1,prev_x2,prev_y2)
                    possible_moves,prev_x1,prev_y1,prev_x2,prev_y2 = board.check_down(original_move,possible_moves,i,j,WIN,prev_x1,prev_y1,prev_x2,prev_y2)
                    possible_moves,prev_x1,prev_y1,prev_x2,prev_y2 = board.check_left(original_move,possible_moves,i,j,WIN,prev_x1,prev_y1,prev_x2,prev_y2)
                    possible_moves,prev_x1,prev_y1,prev_x2,prev_y2 = board.check_right(original_move,possible_moves,i,j,WIN,prev_x1,prev_y1,prev_x2,prev_y2)
            if original_move.symmetric:
                # If the move is symmetric it is not needed to rotate the card
                break
            else:
                original_move=original_move.make_symmetric(num)

        board.print(WIN, prev_x1, prev_y1, (193,108,56))
        board.print(WIN, prev_x2, prev_y2, (193,108,56))

        if len(possible_moves)!=0:

            val=float('Inf')
            chosen_move=[]
            for move in possible_moves:
                test_board = deepcopy(board)
                val,chosen_move = test_board.evaluate_moves(move,val,chosen_move)

            move=random.choice(chosen_move)
            best_deck[num] = [move,num,val]

    if len(best_deck.keys())>0:
        val=float('Inf')
        for el in [*best_deck]:
            if best_deck[el][2]<val:
                best_move=best_deck[el][0]
                best_num=best_deck[el][1]
                val=best_deck[el][2]

        board.display_move(best_move,best_num,WIN)

    return board,best_num
