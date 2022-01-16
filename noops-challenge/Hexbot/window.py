import random
import secrets

import requests
from graphics import Circle, GraphWin, Point

from ball import Ball


class Window(GraphWin):
    def __init__(self, width: int, height: int, ticks: int, ballCount: int, speed: int):
        GraphWin.__init__(self, 'hexbot', width, height)
        self.ticks = ticks
        self.ballCount = ballCount
        self.speed = speed
        self.balls = self.generateBalls(self.ballCount)

    def update(self):
        for ball in self.balls:
            for ball in self.balls:
                ball.update()
            for i in range(0, self.ballCount):
                for j in range(i+1, self.ballCount):
                    self.balls[i].handleCollision(self.balls[j])

    def generateBalls(self, numBalls) -> list[Ball]:
        """Generate the list of balls"""

        try:
            request = requests.get(
                'https://api.noopschallenge.com/hexbot?count='+str(numBalls)).json()
            colors = [color['value'] for color in request['colors']]
        except:
            print('Failed to connect, generating random colors')
            colors = ['#'+secrets.token_hex(3) for _ in range(numBalls)]

        curColor = 0
        ballList = []
        while len(ballList) < numBalls:
            rad = random.randint(20, 80)
            posX = random.randint(rad, self.getWidth() - rad)
            posY = random.randint(rad, self.getHeight() - rad)
            velX = random.randint(-self.speed, self.speed)/(self.ticks * 2)
            velY = random.randint(-self.speed, self.speed)/(self.ticks * 2)

            circle = Circle(Point(posX, posY), rad)
            circle.setFill(colors[curColor])

            ball = Ball(Point(posX, posY), Point(
                velX, velY), rad, colors[curColor], circle, self)
            collide = False
            for other in ballList:
                if ball.isCollided(other):
                    collide = True
                    break
            if not collide:
                ballList.append(ball)
                circle.draw(self)
                curColor += 1
        return ballList

    @property
    def ticks(self):
        return self.__ticks

    @ticks.setter
    def ticks(self, ticks):
        self.__ticks = ticks

    @property
    def ballCount(self):
        return self.__ballCount

    @ballCount.setter
    def ballCount(self, ballCount):
        self.__ballCount = ballCount

    @property
    def speed(self):
        return self.__speed

    @speed.setter
    def speed(self, speed):
        self.__speed = speed
