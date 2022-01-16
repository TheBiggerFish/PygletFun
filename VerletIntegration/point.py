from math import isclose
from random import uniform
from typing import Optional, Union

import pyglet
from fishpy.geometry import ORIGIN_2D as ORIGIN
from fishpy.geometry import Point2D

from config import *


class Point(Point2D):

    def __init__(self, x: float, y: float, static: bool = False, old: Optional[Point2D] = None, graphics_batch: Optional[pyglet.graphics.Batch] = None, radius: int = DEFAULT_POINT_RADIUS):
        super().__init__(x, y)
        self.static = static

        self.old = Point2D(x, y) if old is None else old
        self.graphic: Optional[pyglet.shapes.Circle] = None
        self.batch = graphics_batch
        self.radius = radius

    @staticmethod
    def _load_velocity(vel: Union[int, dict[str, int]]) -> int:
        if type(vel) in (int, float):
            return vel
        elif 'random' in vel and 'low' in vel['random'] and 'high' in vel['random']:
            range = vel['random']
            return uniform(range['low'], range['high'])
        raise ValueError('Could not parse velocity')

    @classmethod
    def load_config(cls, graphics_batch: pyglet.graphics.Batch, x: float, y: float, visible: bool = VISIBLE_POINTS, static: bool = False, initial_velocity: Optional[dict[str, Union[int, dict[str, int]]]] = None, **kwargs):
        if not visible:
            graphics_batch = None
        if initial_velocity is None:
            old = Point2D(x, y)
        elif 'x' and 'y' in initial_velocity:
            vel_x = Point._load_velocity(initial_velocity['x'])
            vel_y = Point._load_velocity(initial_velocity['y'])
            old = Point2D(x, y) - Point2D(vel_x, vel_y)
        else:
            raise ValueError('Could not parse config for point')
        return cls(x=x, y=y, static=static, old=old, graphics_batch=graphics_batch, **kwargs)

    def update_graphics(self):
        if self.batch is not None:
            self.graphic = pyglet.shapes.Circle(
                self.x, self.y, radius=self.radius, batch=self.batch, color=(0, 0, 0))

    def __repr__(self) -> str:
        return f'Point({self.x},{self.y},old={Point2D.__repr__(self.old)})'

    @property
    def velocity(self):
        return self - self.old

    def update(self):
        if self.static:
            return
        if FLOOR_FRICTION_ENABLED and isclose(self.y, self.old.y, abs_tol=0.5) and isclose(self.y, DEFAULT_POINT_RADIUS, abs_tol=2):
            vel = self.velocity * FRICTION_COEF ** FLOOR_FRICTION_EXP
        else:
            vel = self.velocity * FRICTION_COEF
        self.old = self.copy()
        self.x += vel.x
        self.y += vel.y

        self.y -= GRAVITY

    def restrict(self):
        if self.static or not BOUNDED_WALLS:
            return
        vel = self.velocity * FRICTION_COEF

        lower_bound = ORIGIN + \
            Point2D(self.radius, self.radius)
        upper_bound = WINDOW_SIZE - \
            Point2D(self.radius, self.radius)
        if self.x > upper_bound.x:
            self.x = upper_bound.x
            self.old.x = self.x + vel.x * BOUNCE_COEF
        elif self.x < lower_bound.x:
            self.x = lower_bound.x
            self.old.x = self.x + vel.x * BOUNCE_COEF

        if self.y > upper_bound.y:
            self.y = upper_bound.y
            self.old.y = self.y + vel.y * BOUNCE_COEF
        elif self.y < lower_bound.y:
            self.y = lower_bound.y
            self.old.y = self.y + vel.y * BOUNCE_COEF
