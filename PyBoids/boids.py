import pyglet
from fishpy.geometry import ORIGIN_2D, Point2D
from fishpy.utility.debug import profile

from boid import Boid

WINDOW_SIZE = Point2D(1600, 800)
FPS = 60
BOID_COUNT = 75


batch = pyglet.graphics.Batch()
window = pyglet.window.Window(
    width=WINDOW_SIZE.x, height=WINDOW_SIZE.y, resizable=False)
pyglet.gl.glClearColor(1, 1, 1, 1)

boids: list[Boid] = [Boid(i, pos := Point2D.random(
    ORIGIN_2D, WINDOW_SIZE), pos+Point2D.random(Point2D(-10, -10),
                                                Point2D(10, 10)),
    batch) for i in range(BOID_COUNT)]
# others: list[list[Boid]] = [boids[:i]+boids[i+1:]
#                             for i, _ in enumerate(boids)]


def update(dt):
    window.clear()
    for i, boid in enumerate(boids):
        boid.move(boids)
    batch.draw()


if __name__ == '__main__':
    pyglet.clock.schedule_interval(update, 1/FPS)
    pyglet.app.run()
