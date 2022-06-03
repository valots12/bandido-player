# Auto Bandido player using OpenCV and PyGame

Personal project

The purpose of the project is to create an automatic agent that plays the card game Bandido. It is able to detect the cards passed by the user using OpenCV, recognize the move, and then implement a greedy algorithm to minimize the number of possible exits using the best card out of the three that compose the current deck. Possibile future implementations include the design of a better algorithm able to look some moves forward.

Credits to @EdjeElectronics for flattener and videostream functions.

https://user-images.githubusercontent.com/63108350/171954986-77d9d88e-0d7b-43d6-b1dc-cce7b0b8460e.mp4

Note: the script may be influenced by different lighting conditions. The second parameter of the function cv2.threshold should be adapted using the best value from 0 to 255, in particul for the match_card function at line 115 of Card.py.
