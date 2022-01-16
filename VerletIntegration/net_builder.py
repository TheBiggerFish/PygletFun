
from fishpy.geometry import Point2D

size = Point2D(40, 20)
gaps = Point2D(12, 12)
start = Point2D(100, 150)
static_points = 8


config = '''
constants:
  WINDOW_SIZE: 
    x: 600
    y: 400
  SQUISH_ITERATIONS: 1
  BOUNDED_WALLS: False

'''

lines: list[str] = [config, 'points:\n']

i = 0
for y in range(start.y, start.y+gaps.y*size.y, gaps.y):
    for x in range(start.x, start.x+gaps.x*size.x, gaps.x):
        lines.append(f'  p_{i}:\n')
        lines.append(f'    x: {x}\n')
        lines.append(f'    y: {y}\n')
        if y == start.y+gaps.y*(size.y-1) and x % static_points == 0:
            lines.append(f'    static: True\n')
        i += 1

lines.append('\nsticks:\n')
for i in range(0, size.x*size.y):
    if i % size.x != size.x-1:
        lines.append(f'  - p1: p_{i}\n'
                     f'    p2: p_{i+1}\n')
    if i // size.x != size.y - 1:
        lines.append(f'  - p1: p_{i}\n'
                     f'    p2: p_{i+size.x}\n')


with open('VerletIntegration/configurations/net_(high).yml', 'w+') as f:
    f.writelines(lines)
