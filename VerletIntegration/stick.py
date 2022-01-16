import pyglet
from fishpy.geometry import ORIGIN_2D, LineSegment

from config import WINDOW_SIZE
from point import Point


class Stick:
    def __init__(self, p1: Point, p2: Point, graphics_batch: pyglet.graphics.Batch, visible: bool = True):
        self.p1 = p1
        self.p2 = p2
        self.length = self.dist
        self.batch = graphics_batch if visible else None
        self.graphic = None

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.p1!r},{self.p2!r})'

    @property
    def dist(self):
        return self.p1.euclidean_distance(self.p2)

    def update_graphics(self):
        self.p1.update_graphics()
        self.p2.update_graphics()
        if self.batch:
            if not self.graphic:
                self.graphic = pyglet.shapes.Line(
                    self.p1.x, self.p1.y, self.p2.x, self.p2.y, width=2, color=(0, 0, 0), batch=self.batch)
            else:
                self.graphic.x = self.p1.x
                self.graphic.y = self.p1.y
                self.graphic.x2 = self.p2.x
                self.graphic.y2 = self.p2.y

    def update(self):
        self.restrict()
        self.update_graphics()

    def out_of_range(self) -> bool:
        p1_out = not self.p1.in_bounds(ORIGIN_2D, WINDOW_SIZE)
        p2_out = not self.p2.in_bounds(ORIGIN_2D, WINDOW_SIZE)
        return p1_out and p2_out

    def restrict(self):
        offset = self.p2-self.p1
        difference = self.length-self.dist
        if self.p1.static or self.p2.static:
            percent = difference/self.dist
        else:
            percent = difference/self.dist/2
        offset *= percent

        if not self.p1.static:
            self.p1.x -= offset.x
            self.p1.y -= offset.y
        if not self.p2.static:
            self.p2.x += offset.x
            self.p2.y += offset.y
