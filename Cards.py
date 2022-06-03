# Import necessary packages
import numpy as np
import cv2
import time

### Constants ###

# Adaptive threshold levels
BKG_THRESH = 300
MOVE_DIFF_MAX = float('Inf')

CARD_MAX_AREA = 200000
CARD_MIN_AREA = 100000

font = cv2.FONT_HERSHEY_SIMPLEX

### Structures to hold query card and train card information ###
class Query_card:

    def __init__(self):
        self.contour = [] # Contour of card
        self.width, self.height = 0, 0 # Width and height of card
        self.corner_pts = [] # Corner points of card
        self.center = [] # Center point of card
        self.warp = [] # 300x600, flattened, grayed, blurred image
        self.best_move_match = "Unknown" # Best matched move
        self.move_diff = 0 # Difference between move image and best matched train move image


class Train_moves:

    def __init__(self):
        self.img = [] # Thresholded, sized move image loaded from hard drive
        self.name = "Placeholder"


def load_moves(filepath):
    """Loads move images from directory specified by filepath. Stores
    them in a list of Train_moves objects."""
    train_moves = []
    i = 0
    
    for move in range(1,33):
        train_moves.append(Train_moves())
        train_moves[i].name = 'Move_' + str(move)
        filename = 'Move_' + str(move) + '.png'
        tmp_train = cv2.imread(filepath+filename, cv2.IMREAD_GRAYSCALE)
        retval, train_moves[i].img = cv2.threshold(tmp_train,70,255,cv2.THRESH_BINARY)

        # test = cv2.threshold(tmp_train,70,255,cv2.THRESH_BINARY)

        # cv2.imshow('Output_warp', test)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        i+=1

    return train_moves


def preprocess_image(image):

    """Returns a grayed, blurred, and adaptively thresholded camera image."""
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray,(5,5),0)

    retval, thresh = cv2.threshold(blur,120,255,cv2.THRESH_BINARY)

    return thresh


def find_cards(thresh_image):
    """Finds all card-sized contours in a thresholded camera image.
    Returns the number of cards, and a list of card contours sorted
    from largest to smallest."""

    # Find contours and sort their indices by contour size
    cnts,hier = cv2.findContours(thresh_image,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    index_sort = sorted(range(len(cnts)), key=lambda i : cv2.contourArea(cnts[i]),reverse=True)

    # If there are no contours, do nothing
    if len(cnts) == 0:
        return [], []
    
    # Otherwise, initialize empty sorted contour and hierarchy lists
    cnts_sort = []
    hier_sort = []
    cnt_is_card = np.zeros(len(cnts),dtype=int)

    # Fill empty lists with sorted contour and sorted hierarchy. Now,
    # the indices of the contour list still correspond with those of
    # the hierarchy list. The hierarchy array can be used to check if
    # the contours have parents or not.
    for i in index_sort:
        cnts_sort.append(cnts[i])
        hier_sort.append(hier[0][i])

    # Determine which of the contours are cards by applying the
    # following criteria: 1) Smaller area than the maximum card size,
    # 2) bigger area than the minimum card size

    for i in range(len(cnts_sort)):
        size = cv2.contourArea(cnts_sort[i])     
        # peri = cv2.arcLength(cnts_sort[i],True)
        # approx = cv2.approxPolyDP(cnts_sort[i],0.01*peri,True) 
        # and len(approx)==4
        # and hier_sort[i][3]==-1
        if size < CARD_MAX_AREA and size > CARD_MIN_AREA:
            cnt_is_card[i] = 1

    return cnts_sort, cnt_is_card


def preprocess_card(contour, image):
    """Uses contour to find information about the query card. Isolates move from the card."""

    # Initialize new Query_card object
    qCard = Query_card()

    qCard.contour = contour

    # Find perimeter of card and use it to approximate corner points
    peri = cv2.arcLength(contour,True)
    approx = cv2.approxPolyDP(contour,0.01*peri,True)
    pts = np.float32(approx)
    qCard.corner_pts = pts

    # Find width and height of card's bounding rectangle
    x,y,w,h = cv2.boundingRect(contour)
    qCard.width, qCard.height = w, h

    # Find center point of card by taking x and y average of the four corners.
    average = np.sum(pts, axis=0)/len(pts)
    cent_x = int(average[0][0])
    cent_y = int(average[0][1])
    qCard.center = [cent_x, cent_y]

    # Warp card into 300x600 flattened image using perspective transform
    qCard.warp = flattener(image, pts, w, h)

    return qCard


def match_card(qCard, train_moves):
    """Finds best rank and suit matches for the query card. Differences
    the query card rank and suit images with the train rank and suit images.
    The best match is the rank or suit image that has the least difference."""

    best_move_match_diff = 1000000  
    best_move_match_name = "Unknown"
    i = 0

    # If no contours were found in query card in preprocess_card function,
    # the img size is zero, so skip the differencing process
    # (card will be left as Unknown)
    if (len(qCard.warp) != 0):

        # lower values to descrease the area selected in black
        qCard.warp = cv2.threshold(qCard.warp,20,255,cv2.THRESH_BINARY)[1]

        # cv2.imshow('Output_warp', qCard.warp)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        
        # Difference the query card move image from each of the train move images,
        # and store the result with the least difference
        for Tmove in train_moves:

            diff_img = cv2.absdiff(qCard.warp, Tmove.img)
            move_diff = int(np.sum(diff_img)/255)
            
            if move_diff < best_move_match_diff:
                best_move_match_diff = move_diff
                best_move_name = Tmove.name

            diff_img = cv2.absdiff(qCard.warp, np.rot90(Tmove.img, 2))
            move_diff = int(np.sum(diff_img)/255)
            
            if move_diff < best_move_match_diff:
                best_move_match_diff = move_diff
                best_move_name = Tmove.name

 
    # Combine best rank match and best suit match to get query card's identity.
    # If the best matches have too high of a difference value, card identity
    # is still Unknown
    if (best_move_match_diff < MOVE_DIFF_MAX):
        best_move_match_name = best_move_name

    # Return the identiy of the card and the quality of the move
    return best_move_match_name, best_move_match_diff
    

def draw_results(image, qCard):
    """Draw the card name, center point, and contour on the camera image."""

    x = qCard.center[0]
    y = qCard.center[1]
    cv2.circle(image,(x,y),5,(255,0,0),-1)

    move_name = qCard.best_move_match

    # Draw card name twice, so letters have black outline
    cv2.putText(image,(move_name),(x-60,y-10),font,1,(0,0,0),3,cv2.LINE_AA)
    cv2.putText(image,(move_name),(x-60,y-10),font,1,(50,200,200),2,cv2.LINE_AA)

    return image, move_name


def flattener(image, pts, w, h):
    """Flattens an image of a card into a top-down 200x300 perspective.
    Returns the flattened, re-sized, grayed image.
    See www.pyimagesearch.com/2014/08/25/4-point-opencv-getperspective-transform-example/"""
    temp_rect = np.zeros((4,2), dtype = "float32")
    
    s = np.sum(pts, axis = 2)

    tl = pts[np.argmin(s)]
    br = pts[np.argmax(s)]

    diff = np.diff(pts, axis = -1)
    tr = pts[np.argmin(diff)]
    bl = pts[np.argmax(diff)]

    # Need to create an array listing points in order of
    # [top left, top right, bottom right, bottom left]
    # before doing the perspective transform

    if w <= 0.8*h: # If card is vertically oriented
        temp_rect[0] = tl
        temp_rect[1] = tr
        temp_rect[2] = br
        temp_rect[3] = bl

    if w >= 1.2*h: # If card is horizontally oriented
        temp_rect[0] = bl
        temp_rect[1] = tl
        temp_rect[2] = tr
        temp_rect[3] = br

    # If the card is 'diamond' oriented, a different algorithm
    # has to be used to identify which point is top left, top right
    # bottom left, and bottom right.
    
    if w > 0.8*h and w < 1.2*h: #If card is diamond oriented
        # If furthest left point is higher than furthest right point,
        # card is tilted to the left.
        if pts[1][0][1] <= pts[3][0][1]:
            # If card is titled to the left, approxPolyDP returns points
            # in this order: top right, top left, bottom left, bottom right
            temp_rect[0] = pts[1][0] # Top left
            temp_rect[1] = pts[0][0] # Top right
            temp_rect[2] = pts[3][0] # Bottom right
            temp_rect[3] = pts[2][0] # Bottom left

        # If furthest left point is lower than furthest right point,
        # card is tilted to the right
        if pts[1][0][1] > pts[3][0][1]:
            # If card is titled to the right, approxPolyDP returns points
            # in this order: top left, bottom left, bottom right, top right
            temp_rect[0] = pts[0][0] # Top left
            temp_rect[1] = pts[3][0] # Top right
            temp_rect[2] = pts[2][0] # Bottom right
            temp_rect[3] = pts[1][0] # Bottom left
            
    maxWidth = 300
    maxHeight = 600

    # Create destination array, calculate perspective transform matrix,
    # and warp card image
    dst = np.array([[0,0],[maxWidth-1,0],[maxWidth-1,maxHeight-1],[0, maxHeight-1]], np.float32)
    M = cv2.getPerspectiveTransform(temp_rect,dst)
    warp = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    warp = cv2.cvtColor(warp,cv2.COLOR_BGR2GRAY)

    return warp