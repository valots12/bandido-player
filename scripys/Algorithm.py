from copy import deepcopy
import random
import pygame
import time
from PIL import Image
import MainBandido


class Move:
    def __init__(self,num):

        im = Image.open("./Img/Move_"+str(num)+".png")
        im = im.convert("RGB")
        self.down = im.getpixel((150,575)) == (23, 31, 50)
        self.up = im.getpixel((150,25)) == (23, 31, 50)
        self.left1 = im.getpixel((25,450)) == (23, 31, 50)
        self.left2 = im.getpixel((25,150)) == (23, 31, 50)
        self.right1 = im.getpixel((275,450)) == (23, 31, 50)
        self.right2 = im.getpixel((275,150)) == (23, 31, 50)

        if self.up==self.down and self.left1==self.right2 and self.left2==self.right1:
            self.symmetric = True
        else:
            self.symmetric = False

    def make_symmetric(self,num):
        # Return a symmetric version of the given move
        new_move = Move(num)
        new_move.symmetric = True
        new_move.left1 = self.right2
        new_move.left2 = self.right1
        new_move.right1 = self.left2
        new_move.right2 = self.left1
        new_move.up = self.down
        new_move.down = self.up

        return new_move


class Cell:
    def __init__(self, row, col, SQUARE_SIZE):
        self.row = row
        self.col = col
        self.x = SQUARE_SIZE * col
        self.y = SQUARE_SIZE * row
        self.value = 0
        self.left = False
        self.right = False
        self.up = False
        self.down = False
        self.square_size = SQUARE_SIZE

    def draw(self, win, color):
        pygame.draw.rect(win, color, (self.x, self.y, self.square_size, self.square_size))

    def change_value(self,value):
        self.value = value

    def change_open(self,position,value):
        if position=='UP':
            self.up = value
        elif position=='DOWN':
            self.down = value
        elif position=='LEFT':
            self.left = value
        elif position=='RIGHT':
            self.right = value


class Board:
    def __init__(self,ROWS,COLS,SQUARE_SIZE,WIN,HEIGHT,WIDTH):
        self.board = []
        self.square_size = SQUARE_SIZE
        self.rows = ROWS
        self.cols = COLS
        self.create_board()

        icon = pygame.image.load("./Img/Logo.png")
        pygame.display.set_icon(icon)
        pygame.display.set_caption('Bandido')
        pygame.draw.rect(WIN, (193,108,56), (0,0,WIDTH*2, HEIGHT))
        pygame.display.update()

    def create_board(self):
        for row in range(self.rows):
            self.board.append([])
            for col in range(self.cols):
                self.board[row].append(Cell(row,col,self.square_size))

    def start(self,num,WIN):
        # The starting point is the center of the board
        self.change_value(self.rows//2, self.cols//2-1,2)
        self.change_open(self.rows//2, self.cols//2-1,'UP','True')
        self.change_open(self.rows//2, self.cols//2-1,'DOWN','True')
        if num==2:
            self.change_open(self.rows//2, self.cols//2-1,'LEFT','True')

        self.change_value(self.rows//2, self.cols//2,2)
        self.change_open(self.rows//2, self.cols//2,'UP','True')
        self.change_open(self.rows//2, self.cols//2,'RIGHT','True')
        self.change_open(self.rows//2, self.cols//2,'DOWN','True')

        pic = pygame.image.load("./Img/Move_"+str(num)+".png")
        pic = pygame.transform.rotate(pic, 90)
        WIN.blit(pygame.transform.scale(pic, (self.square_size*2, self.square_size)), 
                (int(self.get_value(self.rows//2, self.cols//2-1,'x')), int(self.get_value(self.rows//2, self.cols//2-1,'y'))))
        pygame.display.update()

    def print(self,win,row,col,color):
        self.board[row][col].draw(win, color)

    def change_value(self,row,col,value):
        self.board[row][col].change_value(value)

    def change_open(self,row,col,position,value):
        self.board[row][col].change_open(position,value)

    def get_value(self,row,col,attribute):
        return str(getattr(self.board[row][col],attribute))

    def evaluate(self):
        # Return the number of open roads in the board
        count=0
        for i in range(self.rows):
            for j in range(self.cols):  
                if j>0:
                    if getattr(self.board[i][j],'left') and int(getattr(self.board[i][j-1],'value'))<2:
                        count+=1
                else:
                    if getattr(self.board[i][j],'left'):
                        count+=1
                if j<(self.cols-1):
                    if getattr(self.board[i][j],'right') and int(getattr(self.board[i][j+1],'value'))<2:
                        count+=1
                else:
                    if getattr(self.board[i][j],'right'):
                        count+=1
                if i>0:
                    if getattr(self.board[i][j],'up') and int(getattr(self.board[i-1][j],'value'))<2:
                        count+=1
                else:
                    if getattr(self.board[i][j],'up'):
                        count+=1
                if i<(self.rows-1):
                    if getattr(self.board[i][j],'down') and int(getattr(self.board[i+1][j],'value'))<2:
                        count+=1
                else:
                    if getattr(self.board[i][j],'down'):
                        count+=1
        return count

    def possible_cells(self):
        # Assign a value of 1 to cells that are free and near to a used cell in at least one of the four border
        for i in range(self.rows):
            for j in range(self.cols):  
                mutate=False 
                if int(self.get_value(i,j,'value'))==0:
                    if i>0:
                        if int(self.get_value(i-1,j,'value'))==2:
                            mutate=True
                    if j>0:
                        if int(self.get_value(i,j-1,'value'))==2:
                            mutate=True
                    if i<(self.rows-1):
                        if int(self.get_value(i+1,j,'value'))==2:
                            mutate=True
                    if j<(self.cols-1):
                        if int(self.get_value(i,j+1,'value'))==2:
                            mutate=True
                    if mutate:
                        self.change_value(i,j,1)

    def change_open_multiple(self,move):

        if move[2]=='UP':
            self.change_open(move[0][0],move[0][1],'DOWN',move[3].down)
            self.change_open(move[0][0],move[0][1],'LEFT',move[3].left1)
            self.change_open(move[0][0],move[0][1],'RIGHT',move[3].right1)
            self.change_open(move[1][0],move[1][1],'UP',move[3].up)
            self.change_open(move[1][0],move[1][1],'LEFT',move[3].left2)
            self.change_open(move[1][0],move[1][1],'RIGHT',move[3].right2)

        elif move[2]=='DOWN':
            self.change_open(move[0][0],move[0][1],'UP',move[3].up)
            self.change_open(move[0][0],move[0][1],'LEFT',move[3].left2)
            self.change_open(move[0][0],move[0][1],'RIGHT',move[3].right2)
            self.change_open(move[1][0],move[1][1],'DOWN',move[3].down)
            self.change_open(move[1][0],move[1][1],'LEFT',move[3].left1)
            self.change_open(move[1][0],move[1][1],'RIGHT',move[3].right1)

        elif move[2]=='LEFT':
            self.change_open(move[0][0],move[0][1],'RIGHT',move[3].down)
            self.change_open(move[0][0],move[0][1],'UP',move[3].right1)
            self.change_open(move[0][0],move[0][1],'DOWN',move[3].left1)
            self.change_open(move[1][0],move[1][1],'LEFT',move[3].up)
            self.change_open(move[1][0],move[1][1],'UP',move[3].right2)
            self.change_open(move[1][0],move[1][1],'DOWN',move[3].left2)  

        elif move[2]=='RIGHT':
            self.change_open(move[0][0],move[0][1],'LEFT',move[3].down)
            self.change_open(move[0][0],move[0][1],'UP',move[3].left1)
            self.change_open(move[0][0],move[0][1],'DOWN',move[3].right1)
            self.change_open(move[1][0],move[1][1],'RIGHT',move[3].up)
            self.change_open(move[1][0],move[1][1],'UP',move[3].left2)
            self.change_open(move[1][0],move[1][1],'DOWN',move[3].right2)  

    def check_availability(self,move):
        # A move is defined as not available if it causes the creation of a 1x1 square surrounded in all directions and with at least one open road
        self.change_value(move[0][0],move[0][1],2)
        self.change_value(move[1][0],move[1][1],2)
        self.change_open_multiple(move)

        for row in range(1,self.rows-1):
            for col in range(1,self.cols-1):
                if int(self.get_value(row,col,'value'))<2 and int(self.get_value(row+1,col,'value'))==2 and int(self.get_value(row-1,col,'value'))==2 and int(self.get_value(row,col+1,'value'))==2 and int(self.get_value(row,col-1,'value'))==2: 
                    if self.get_value(row+1,col,'up')=='True' or self.get_value(row+1,col,'up')=='True' or self.get_value(row-1,col,'down') or self.get_value(row,col+1,'left') or self.get_value(row,col-1,'right'):
                        return False

        return True

    def check_up(self,current_move,possible_moves,i,j,WIN,prev_x1,prev_y1,prev_x2,prev_y2):
        # Check possibility of moving up
        if i>0 and self.get_value(i,j,'value')=='1':
            if int(self.get_value(i-1,j,'value'))<2:
                available=True
                if i<(self.rows-1):
                    if self.get_value(i+1,j,'up')!=str(current_move.down) and int(self.get_value(i+1,j,'value'))>1:
                        available=False
                if j>0:
                    if self.get_value(i,j-1,'right')!=str(current_move.left1) and int(self.get_value(i,j-1,'value'))>1:
                        available=False
                    if self.get_value(i-1,j-1,'right')!=str(current_move.left2) and int(self.get_value(i-1,j-1,'value'))>1:
                        available=False
                if i>1:
                    if self.get_value(i-2,j,'down')!=str(current_move.up) and int(self.get_value(i-2,j,'value'))>1:
                        available=False
                if j<(self.cols-1):
                    if self.get_value(i,j+1,'left')!=str(current_move.right1) and int(self.get_value(i,j+1,'value'))>1:
                        available=False
                    if self.get_value(i-1,j+1,'left')!=str(current_move.right2) and int(self.get_value(i-1,j+1,'value'))>1:
                        available=False

                if available:
                    test_board = deepcopy(self)
                    if test_board.check_availability([[i,j],[i-1,j],'UP',current_move]):
                        possible_moves.append([[i,j],[i-1,j],'UP',current_move])
                        if prev_x1 != -1:
                            self.print(WIN, prev_x1, prev_y1, (193,108,56))
                            self.print(WIN, prev_x2, prev_y2, (193,108,56))
                        self.print(WIN, i, j, (122,122,122))
                        self.print(WIN, i-1, j, (122,122,122))
                        pygame.display.update()
                        prev_x1 = i
                        prev_y1 = j
                        prev_x2 = i-1
                        prev_y2 = j
                        time.sleep(0.05)
        return possible_moves,prev_x1,prev_y1,prev_x2,prev_y2

    def check_down(self,current_move,possible_moves,i,j,WIN,prev_x1,prev_y1,prev_x2,prev_y2):
        # Check possibility of moving down
        if i<(self.rows-1) and self.get_value(i,j,'value')=='1':
            if int(self.get_value(i+1,j,'value'))<2:
                available=True
                if i>0:
                    if self.get_value(i-1,j,'down')!=str(current_move.up) and int(self.get_value(i-1,j,'value'))>1:
                        available=False
                if j>0:
                    if self.get_value(i,j-1,'right')!=str(current_move.left2) and int(self.get_value(i,j-1,'value'))>1:
                        available=False
                    if self.get_value(i+1,j-1,'right')!=str(current_move.left1) and int(self.get_value(i+1,j-1,'value'))>1:
                        available=False
                if i<(self.rows-2):
                    if self.get_value(i+2,j,'up')!=str(current_move.down) and int(self.get_value(i+2,j,'value'))>1:
                        available=False
                if j<(self.cols-1):
                    if self.get_value(i,j+1,'left')!=str(current_move.right2) and int(self.get_value(i,j+1,'value'))>1:
                        available=False
                    if self.get_value(i+1,j+1,'left')!=str(current_move.right1) and int(self.get_value(i+1,j+1,'value'))>1:
                        available=False

                if available:
                    test_board = deepcopy(self)
                    if test_board.check_availability([[i,j],[i+1,j],'DOWN',current_move]):
                        possible_moves.append([[i,j],[i+1,j],'DOWN',current_move])
                        if prev_x1 != -1:
                            self.print(WIN, prev_x1, prev_y1, (193,108,56))
                            self.print(WIN, prev_x2, prev_y2, (193,108,56))
                        self.print(WIN, i, j, (122,122,122))
                        self.print(WIN, i+1, j, (122,122,122))
                        pygame.display.update()
                        prev_x1 = i
                        prev_y1 = j
                        prev_x2 = i+1
                        prev_y2 = j
                        time.sleep(0.05)
        return possible_moves,prev_x1,prev_y1,prev_x2,prev_y2

    def check_left(self,current_move,possible_moves,i,j,WIN,prev_x1,prev_y1,prev_x2,prev_y2):
        # Check possibility of moving left
        if j>0 and self.get_value(i,j,'value')=='1':
            if int(self.get_value(i,j-1,'value'))<2:
                available=True
                if j<(self.cols-1):
                    if self.get_value(i,j+1,'left')!=str(current_move.down) and int(self.get_value(i,j+1,'value'))>1:
                        available=False
                if i>0:
                    if self.get_value(i-1,j,'down')!=str(current_move.right1) and int(self.get_value(i-1,j,'value'))>1:
                        available=False
                    if self.get_value(i-1,j-1,'down')!=str(current_move.right2) and int(self.get_value(i-1,j-1,'value'))>1:
                        available=False
                if j>1:
                    if self.get_value(i,j-2,'right')!=str(current_move.up) and int(self.get_value(i,j-2,'value'))>1:
                        available=False
                if i<(self.rows-1):
                    if self.get_value(i+1,j,'up')!=str(current_move.left1) and int(self.get_value(i+1,j,'value'))>1:
                        available=False
                    if self.get_value(i+1,j-1,'up')!=str(current_move.left2) and int(self.get_value(i+1,j-1,'value'))>1:
                        available=False
                
                if available:
                    test_board = deepcopy(self)
                    if test_board.check_availability([[i,j],[i,j-1],'LEFT',current_move]):
                        possible_moves.append([[i,j],[i,j-1],'LEFT',current_move])
                        if prev_x1 != -1:
                            self.print(WIN, prev_x1, prev_y1, (193,108,56))
                            self.print(WIN, prev_x2, prev_y2, (193,108,56))
                        self.print(WIN, i, j, (122,122,122))
                        self.print(WIN, i, j-1, (122,122,122))
                        pygame.display.update()
                        prev_x1 = i
                        prev_y1 = j
                        prev_x2 = i
                        prev_y2 = j-1
                        time.sleep(0.05)
        return possible_moves,prev_x1,prev_y1,prev_x2,prev_y2

    def check_right(self,current_move,possible_moves,i,j,WIN,prev_x1,prev_y1,prev_x2,prev_y2):
        # Check possibility of moving right
        if j<(self.cols-1) and self.get_value(i,j,'value')=='1':
            if int(self.get_value(i,j+1,'value'))<2:
                available=True
                if j>0:
                    if self.get_value(i,j-1,'right')!=str(current_move.down) and int(self.get_value(i,j-1,'value'))>1:
                        available=False
                if i>0:
                    if self.get_value(i-1,j,'down')!=str(current_move.left1) and int(self.get_value(i-1,j,'value'))>1:
                        available=False
                    if self.get_value(i-1,j+1,'down')!=str(current_move.left2) and int(self.get_value(i-1,j+1,'value'))>1:
                        available=False
                if j<(self.cols-2):
                    if self.get_value(i,j+2,'left')!=str(current_move.up) and int(self.get_value(i,j+2,'value'))>1:
                        available=False
                if i<(self.rows-1):
                    if self.get_value(i+1,j,'up')!=str(current_move.right1) and int(self.get_value(i+1,j,'value'))>1:
                        available=False
                    if self.get_value(i+1,j+1,'up')!=str(current_move.right2) and int(self.get_value(i+1,j+1,'value'))>1:
                        available=False

                if available:
                    test_board = deepcopy(self)
                    if test_board.check_availability([[i,j],[i,j+1],'UP',current_move]):
                        possible_moves.append([[i,j],[i,j+1],'RIGHT',current_move])
                        if prev_x1 != -1:
                            self.print(WIN, prev_x1, prev_y1, (193,108,56))
                            self.print(WIN, prev_x2, prev_y2, (193,108,56))
                        self.print(WIN, i, j, (122,122,122))
                        self.print(WIN, i, j+1, (122,122,122))
                        pygame.display.update()
                        prev_x1 = i
                        prev_y1 = j
                        prev_x2 = i
                        prev_y2 = j+1
                        time.sleep(0.05)
        return possible_moves,prev_x1,prev_y1,prev_x2,prev_y2

    def evaluate_moves(self,move,val,chosen_move):
        # Apply the input move to the board and evaluate if it is the best one or not
        self.change_value(move[0][0],move[0][1],2)
        self.change_value(move[1][0],move[1][1],2)

        if move[2]=='UP':
            self.change_open(move[0][0],move[0][1],'DOWN',move[3].down)
            self.change_open(move[0][0],move[0][1],'LEFT',move[3].left1)
            self.change_open(move[0][0],move[0][1],'RIGHT',move[3].right1)
            self.change_open(move[1][0],move[1][1],'UP',move[3].up)
            self.change_open(move[1][0],move[1][1],'LEFT',move[3].left2)
            self.change_open(move[1][0],move[1][1],'RIGHT',move[3].right2)

        elif move[2]=='DOWN':
            self.change_open(move[0][0],move[0][1],'UP',move[3].up)
            self.change_open(move[0][0],move[0][1],'LEFT',move[3].left2)
            self.change_open(move[0][0],move[0][1],'RIGHT',move[3].right2)
            self.change_open(move[1][0],move[1][1],'DOWN',move[3].down)
            self.change_open(move[1][0],move[1][1],'LEFT',move[3].left1)
            self.change_open(move[1][0],move[1][1],'RIGHT',move[3].right1) 

        elif move[2]=='LEFT':
            self.change_open(move[0][0],move[0][1],'RIGHT',move[3].down)
            self.change_open(move[0][0],move[0][1],'UP',move[3].right1)
            self.change_open(move[0][0],move[0][1],'DOWN',move[3].left1)
            self.change_open(move[1][0],move[1][1],'LEFT',move[3].up)
            self.change_open(move[1][0],move[1][1],'UP',move[3].right2)
            self.change_open(move[1][0],move[1][1],'DOWN',move[3].left2)   

        elif move[2]=='RIGHT':
            self.change_open(move[0][0],move[0][1],'LEFT',move[3].down)
            self.change_open(move[0][0],move[0][1],'UP',move[3].left1)
            self.change_open(move[0][0],move[0][1],'DOWN',move[3].right1)
            self.change_open(move[1][0],move[1][1],'RIGHT',move[3].up)
            self.change_open(move[1][0],move[1][1],'UP',move[3].left2)
            self.change_open(move[1][0],move[1][1],'DOWN',move[3].right2)  

        test_val = self.evaluate()
        if test_val < val:
            val = test_val
            chosen_move=[move]
        elif test_val==val:
            chosen_move.append(move)
        return val,chosen_move

    def display_move(self,move,num,WIN):
        # Display the chosen move in the board
        for i in range(self.rows):
            for j in range(self.cols):
                if int(self.get_value(i,j,'value'))==1:
                    self.change_value(i,j,0)

        self.change_value(move[0][0],move[0][1],2)
        self.change_value(move[1][0],move[1][1],2)

        pic = pygame.image.load("./Img/Move_"+str(num)+".png")
        if move[3].symmetric==True:
            pic = pygame.transform.rotate(pic, 180)

        self.change_open_multiple(move)  

        if move[2]=='UP':
            WIN.blit(pygame.transform.scale(pic, (self.square_size, self.square_size*2)), (int(self.get_value(move[1][0],move[1][1],'x')), int(self.get_value(move[1][0],move[1][1],'y'))))

        elif move[2]=='DOWN':
            WIN.blit(pygame.transform.scale(pic, (self.square_size, self.square_size*2)), (int(self.get_value(move[0][0],move[0][1],'x')), int(self.get_value(move[0][0],move[0][1],'y'))))

        elif move[2]=='LEFT':
            pic = pygame.transform.rotate(pic, 90)
            WIN.blit(pygame.transform.scale(pic, (self.square_size*2, self.square_size)), (int(self.get_value(move[1][0],move[1][1],'x')), int(self.get_value(move[1][0],move[1][1],'y'))))

        elif move[2]=='RIGHT':
            pic = pygame.transform.rotate(pic, -90)
            WIN.blit(pygame.transform.scale(pic, (self.square_size*2, self.square_size)), (int(self.get_value(move[0][0],move[0][1],'x')), int(self.get_value(move[0][0],move[0][1],'y'))))

        pygame.display.update()
        time.sleep(0.5)


def cvimage_to_pygame(image):
    # Convert from cvimage to pygame image
    return pygame.image.frombuffer(image.tostring(), image.shape[1::-1],"RGB")


def create_deck(WIN,WIDTH,HEIGHT,SQUARE_SIZE):
    # Creation of the current deck of 3 cards
    history = {}
    deck = {'position_1':[0,WIDTH*1.15],'position_2':[0,WIDTH*1.45],'position_3':[0,WIDTH*1.75]}

    pygame.font.init()
    font = pygame.font.SysFont('CenturyGothic', 25)
    text = font.render('CURRENT DECK', True, (0, 0, 0))
    text_rect = text.get_rect(center=(WIDTH*1.5, HEIGHT*0.65))
    WIN.blit(text, text_rect)
    pygame.draw.rect(WIN, (23, 31, 50), (WIDTH*1.15,HEIGHT*0.7,SQUARE_SIZE*1.2,SQUARE_SIZE*2.4))
    pygame.draw.rect(WIN, (23, 31, 50), (WIDTH*1.45,HEIGHT*0.7,SQUARE_SIZE*1.2,SQUARE_SIZE*2.4))
    pygame.draw.rect(WIN, (23, 31, 50), (WIDTH*1.75,HEIGHT*0.7,SQUARE_SIZE*1.2,SQUARE_SIZE*2.4))
    pygame.display.update()

    return history,deck


def update_deck(deck,num,board,WIN,SQUARE_SIZE,HEIGHT,ROWS,COLS):
    # Update the current deck. If it is composed by three cards, the algorithm starts 
    pic = pygame.image.load("./Img/Move_"+str(num)+".png")
    if deck['position_1'][0]==0:
        deck['position_1'][0] = num
        WIN.blit(pygame.transform.scale(pic, (SQUARE_SIZE*1.2,SQUARE_SIZE*2.4)), (deck['position_1'][1],HEIGHT*0.7))
    elif deck['position_2'][0]==0:
        deck['position_2'][0] = num
        WIN.blit(pygame.transform.scale(pic, (SQUARE_SIZE*1.2,SQUARE_SIZE*2.4)), (deck['position_2'][1],HEIGHT*0.7))
    else:
        deck['position_3'][0] = num
        WIN.blit(pygame.transform.scale(pic, (SQUARE_SIZE*1.2,SQUARE_SIZE*2.4)), (deck['position_3'][1],HEIGHT*0.7))
    pygame.display.update()

    if deck['position_1'][0]>0 and deck['position_2'][0]>0 and deck['position_3'][0]>0:
        board,chosen_position = MainBandido.update([deck['position_1'][0],deck['position_2'][0],deck['position_3'][0]],board,WIN,ROWS,COLS)
        for i in [*deck]:
            if deck[i][0]==chosen_position:
                chosen_card=i
        pygame.draw.rect(WIN, (23, 31, 50), (deck[chosen_card][1],HEIGHT*0.7,SQUARE_SIZE*1.2,SQUARE_SIZE*2.4))
        pygame.display.update()
        deck[chosen_card][0]=0

    time.sleep(1)
    return deck
