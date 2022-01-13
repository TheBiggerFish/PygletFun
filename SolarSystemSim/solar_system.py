from math import cos, sin

import pyglet
from fishpy.geometry import Point2D, Vector2D

from body import Body, BodyType

FPS = 120

WINDOW_SIZE = Point2D(1000, 1000)


window = pyglet.window.Window(
    width=WINDOW_SIZE.x, height=WINDOW_SIZE.y, resizable=False)
batch = pyglet.graphics.Batch()
center = WINDOW_SIZE/2
# sun = pyglet.shapes.Circle(center.x, center.y, radius=100,
#                            color=[255, 255, 0, 2], batch=batch)

sun = Body(100, color=(255, 255, 0), pos=center,
           type=BodyType.SUN, static=False, batch=batch)
planet1 = Body(15, color=(0, 255, 128), pos=center+Point2D(450, 0),
               type=BodyType.PLANET, batch=batch, vel=Vector2D(0, -1.5))
planet2 = Body(10, color=(200, 10, 50), pos=center-Point2D(300, 0),
               type=BodyType.PLANET, batch=batch, vel=Vector2D(0, 2))
moon = Body(2, color=(200, 200, 200), pos=planet1.position+Point2D(30, 0),
            type=BodyType.MOON, batch=batch, vel=Vector2D(0, -2))

bodies = [sun, planet1, planet2, moon]


def update(dt):
    for i, body in enumerate(bodies):
        body.step()
        body.gravitational_acceleration(bodies[:i]+bodies[i+1:])

    sun.step()
    planet1.step()
    planet2.step()
    sun.gravitational_acceleration([planet1, planet2])
    planet1.gravitational_acceleration([sun, planet2])
    planet2.gravitational_acceleration([sun, planet1])
    window.clear()
    batch.draw()


if __name__ == '__main__':
    pyglet.clock.schedule_interval(update, 1/FPS)
    pyglet.app.run()
