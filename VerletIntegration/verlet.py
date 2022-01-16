import pyglet
from fishpy.geometry import ORIGIN_2D, LineSegment, Point2D
from pyglet.window import mouse

from config import CONFIG, FPS, SQUISH_ITERATIONS, WINDOW_SIZE
from point import Point
from stick import Stick
from VerletIntegration.config import BOUNDED_WALLS

batch = pyglet.graphics.Batch()
window = pyglet.window.Window(
    width=WINDOW_SIZE.x, height=WINDOW_SIZE.y, resizable=False)
pyglet.gl.glClearColor(1, 1, 1, 1)
selected_point = None


points: dict[str, Point] = {p: Point.load_config(
    batch, **CONFIG['points'][p]) for p in CONFIG['points']}

sticks: list[Stick] = [
    Stick(points[s['p1']],
          points[s['p2']],
          visible=s.get('visible', True),
          graphics_batch=batch) for s in CONFIG['sticks']]


@window.event
def on_mouse_press(x, y, buttons, modifiers):
    global selected_point

    pos = Point2D(x, y)
    if buttons & mouse.LEFT:
        if selected_point is not None:
            return

        dist, point = min([(point.euclidean_distance(pos), point)
                           for point in points.values()])
        if dist < point.radius or dist < 10:
            selected_point = point
            selected_point.before_selected_status = selected_point.static
            selected_point.static = True
    elif buttons & mouse.RIGHT:
        if selected_point is None:
            dist, point = min([(point.euclidean_distance(pos), point)
                               for point in points.values()])
            if dist < point.radius or dist < 10:
                if selected_point is not point:
                    point.static = not point.static
        else:
            selected_point.before_selected_status = not selected_point.before_selected_status


@window.event
def on_mouse_release(x, y, buttons, modifiers):
    global selected_point
    if selected_point is not None and buttons & mouse.LEFT:
        selected_point.x = x
        selected_point.y = y
        selected_point.static = selected_point.before_selected_status
        del selected_point.before_selected_status
        selected_point = None


@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    if not buttons & mouse.LEFT:
        return
    if selected_point is None:
        line = LineSegment(Point2D(x, y), Point2D(x+dx, y+dy))
        for i, stick in enumerate(sticks):
            if line.intersects(stick):
                if hasattr(sticks[i].p1, 'graphic'):
                    del sticks[i].p1.graphic
                if hasattr(sticks[i].p2, 'graphic'):
                    del sticks[i].p2.graphic
                del sticks[i]
                break
    else:
        selected_point.old.x = x-dx
        selected_point.old.y = y-dy
        selected_point.x = x
        selected_point.y = y


# @profile
def update(dt):
    window.clear()
    for point in points:
        points[point].update()
    # print(points['p_0'], points['p_0'].in_bounds(
    #     ORIGIN_2D, WINDOW_SIZE), ORIGIN_2D, WINDOW_SIZE)
    for _ in range(SQUISH_ITERATIONS):
        out_of_range = set()
        for i, stick in enumerate(sticks):
            stick.update()
            if stick.out_of_range():
                print('stick out')
                out_of_range.add(i)
        if BOUNDED_WALLS:
            for point in points:
                points[point].restrict()
        else:
            for i in sorted(out_of_range, reverse=True):
                print(f'Deleting stick {i}')
                del sticks[i]
    batch.draw()


if __name__ == '__main__':
    pyglet.clock.schedule_interval(update, 1/FPS)
    pyglet.app.run()
