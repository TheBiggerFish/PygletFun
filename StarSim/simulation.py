import pyglet
from fishpy.geometry import Point2D, Vector2D

from star import Star

SIMULATION_RATE = 50
STAR_DENSITY = 0.003

WINDOW_SIZE = Point2D(800, 800)
window = pyglet.window.Window(
    width=WINDOW_SIZE.x, height=WINDOW_SIZE.y, resizable=False)
batch = pyglet.graphics.Batch()

stars: list[Star] = []
for i in range(int(STAR_DENSITY * Vector2D.from_point(WINDOW_SIZE).area())):
    stars.append(Star.random_star(WINDOW_SIZE, batch))

comets = []


def update(_):
    for star in stars:
        star.twinkle()
    window.clear()
    batch.draw()


if __name__ == '__main__':
    pyglet.clock.schedule_interval(update, 1/SIMULATION_RATE)
    pyglet.app.run()
