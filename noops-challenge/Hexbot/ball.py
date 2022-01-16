import math

from colour import Color
from graphics import Circle, GraphWin, Point


class Ball:
    def __init__(self, pos, vel, rad, color, graphic, window):
        self.rad: int = rad
        self.window: GraphWin = window
        self.vel: Point = vel
        self.pos: Point = pos
        self.color: Color = color
        self.graphic: Circle = graphic

    def __str__(self):
        return "Position: " + str(self.pos) + "\t\t|\tVelocity: " + str(self.vel) + "\t\t|\tRadius: " + str(self.rad)

    def __moveBall(self, pos):
        """Move a graphic to a particular position on the window,
        rather than move by an amount"""
        old = self.graphic
        graphic = Circle(pos, self.rad)
        graphic.draw(self.window)
        self.graphic = graphic
        old.undraw()

    def reverse(self, dir):
        """Reverse motion of ball on given axis"""
        if dir == 'x':
            self.vel.x = 0 - self.vel.x
        elif dir == 'y':
            self.vel.y = 0 - self.vel.y

    def update(self):
        """Update position of ball, turning the ball around if it
        gets too close to an edge"""
        tempPos = Point(0, 0)
        tempPos.x = self.pos.x + self.vel.x
        tempPos.y = self.pos.y + self.vel.y
        self.pos = tempPos
        self.__moveBall(self.pos)

    def distance(self, other):
        """Get distance between two balls"""
        assert type(other) is Ball
        xDist = self.pos.x - other.pos.x
        yDist = self.pos.y - other.pos.y
        dist = math.hypot(xDist, yDist)
        return dist

    def isCollided(self, other):
        """Determine if two balls are overlapping or colliding"""
        assert type(other) is Ball
        radii = self.rad + other.rad
        if radii >= self.distance(other):
            return True
        return False

    def handleCollision(self, other):
        """Perform physics on ball if in contact with another ball"""
        if not self.isCollided(other):
            return

        m1 = math.pi * math.pow(self.rad, 2)
        v1 = math.hypot(self.vel.x, self.vel.y)
        t1 = math.atan2(self.vel.y, self.vel.x)

        m2 = math.pi * math.pow(other.rad, 2)
        v2 = math.hypot(other.vel.x, other.vel.y)
        t2 = math.atan2(other.vel.y, other.vel.x)

        distX = self.pos.x - other.pos.x
        distY = self.pos.y - other.pos.y
        phi = math.atan2(distY, distX)

        v1f = ((v1 * math.cos(t1 - phi) * (m1 - m2)) +
               (2 * m2 * v2 * math.cos(t2 - phi))) / (m1 + m2)
        v1xf = (v1f * math.cos(phi)) + \
            (v1 * math.sin(t1 - phi) * math.cos(phi + (math.pi/2)))
        v1yf = (v1f * math.sin(phi)) + \
            (v1 * math.sin(t1 - phi) * math.sin(phi + (math.pi/2)))
        v1F = Point(v1xf, v1yf)

        v2f = ((v2 * math.cos(t2 - phi) * (m2 - m1)) +
               (2 * m1 * v1 * math.cos(t1 - phi))) / (m2 + m1)
        v2xf = (v2f * math.cos(phi)) + \
            (v2 * math.sin(t2 - phi) * math.cos(phi + (math.pi/2)))
        v2yf = (v2f * math.sin(phi)) + \
            (v2 * math.sin(t2 - phi) * math.sin(phi + (math.pi/2)))
        v2F = Point(v2xf, v2yf)

        self.vel = v1F
        other.vel = v2F

    @property
    def pos(self):
        return self.__pos

    @pos.setter
    def pos(self, pos):
        if pos.x < self.rad:
            pos.x = self.rad
            self.reverse('x')
        if pos.y < self.rad:
            pos.y = self.rad
            self.reverse('y')
        if pos.x > (self.window.getWidth() - self.rad):
            pos.x = (self.window.getWidth() - self.rad)
            self.reverse('x')
        if pos.y > (self.window.getHeight() - self.rad):
            pos.y = (self.window.getHeight() - self.rad)
            self.reverse('y')
        self.__pos = pos

    @property
    def vel(self):
        return self.__vel

    @vel.setter
    def vel(self, vel):
        self.__vel = vel

    @property
    def rad(self):
        return self.__rad

    @rad.setter
    def rad(self, rad):
        self.__rad = rad

    @property
    def color(self):
        return self.__color

    @color.setter
    def color(self, color):
        self.__color = color
        return self

    @property
    def graphic(self):
        return self.__graphic

    @graphic.setter
    def graphic(self, graphic):
        graphic.setFill(self.color)
        self.__graphic = graphic

    @property
    def window(self):
        return self.__window

    @window.setter
    def window(self, window):
        self.__window = window
