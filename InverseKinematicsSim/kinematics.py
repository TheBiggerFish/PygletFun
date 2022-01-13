import pyglet
from fishpy.geometry import Point2D

from objects import Joint, Leg

FPS = 60  # Aspirational
SEGMENTS = 100
FABRIK_ITERATIONS = 10

WINDOW_SIZE = Point2D(1920, 1080)

window = pyglet.window.Window(
    width=WINDOW_SIZE.x, height=WINDOW_SIZE.y, resizable=False)
pyglet.gl.glClearColor(1, 1, 1, 1)
batch = pyglet.graphics.Batch()


ORIGIN = Joint(WINDOW_SIZE.x/2, WINDOW_SIZE.y/2, batch)
leg = Leg.generate_leg(25, SEGMENTS+1, ORIGIN, batch)
target = Point2D(0, 0)


def update(_):
    global leg
    leg = leg.execute_fabrik(target)
    window.clear()
    batch.draw()


@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    global target
    target = Point2D(x, y)


if __name__ == '__main__':
    pyglet.clock.schedule_interval(update, 1/FPS)
    pyglet.app.run()
