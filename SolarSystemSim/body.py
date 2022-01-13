from enum import Enum
from math import pi
from typing import Optional

import pyglet
from fishpy.geometry import Point2D, Vector2D
from fishpy.physics import MassiveObject


class BodyType(Enum):
    SUN = 1
    PLANET = 2
    MOON = 3
    STAR = 4


class Body(MassiveObject):
    def __init__(self, radius: int, color: tuple, pos: Point2D, type: BodyType,
                 batch: pyglet.graphics.Batch, vel: Vector2D = Vector2D(0, 0),
                 static: bool = False):
        mass = radius * radius * pi
        super().__init__(mass, position=pos, velocity=vel)
        self.radius = radius
        self.color = color
        self.type = type
        self.static = static
        self.graphic = pyglet.shapes.Circle(
            pos.x, pos.y, radius, color=color, batch=batch)

    def step(self):
        if not self.static:
            super().step()
            self.graphic.x = self.position.x
            self.graphic.y = self.position.y

    def gravitational_acceleration(self, others: list['Body']):
        self.acceleration = Vector2D(0, 0)
        for body in others:
            self.acceleration += super().gravitational_acceleration(body, G=0.05)

    @staticmethod
    def new_sun(radius: int, color: Optional[tuple]):
        pass
