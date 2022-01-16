import json
import time

import requests
from graphics import *
from pynput.mouse import Listener

import Ball

win = GraphWin('hexbot',900,600)
ticks = 30
balls = []
box = Polygon(Point(900,500))

def on_move(x, y):
    pass

def on_click(x, y, button, pressed):
    if pressed:
        print(x,y)



def handleCollisions():
    for i in range(0,len(balls)):
        for j in range(i+1,len(balls)):
            if balls[i].isCollided(balls[j]):
                balls[i].handleCollision(balls[j])

def main():
    with Listener(on_move=on_move, on_click=on_click) as listener:
        listener.join()
        while win.isOpen():
            try:
#                for ball in balls:
#                    handleCollisions()
#                    for ball in balls:
#                        ball.update()
                updateAim()
            except:
                pass
            time.sleep(1/ticks)


main()
