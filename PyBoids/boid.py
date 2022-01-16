import pyglet
from fishpy.geometry import ORIGIN_2D, Point2D, Vector2D

WINDOW_SIZE = Point2D(1600, 800)

SEPARATION_FACTOR = 0.1
SEPARATION_DISTANCE = 30
ALIGNMENT_FACTOR = 0.125
COHESION_FACTOR = 0.005

VIEW_DISTANCE = 100
REMAIN_FACTOR = 1
SPEED_LIMIT = 20

REMAIN_FORCE = 10

GOAL_POSITION = WINDOW_SIZE/2
GOAL_FACTOR = 0.001


class Boid:
    def __init__(self, id_: int, pos: Point2D, old: Point2D, batch: pyglet.graphics.Batch):
        self.id = id_
        self.pos = pos
        self.old = old
        self.graphics = pyglet.shapes.Circle(
            pos.x, pos.y, radius=5, color=(0, 0, 255), batch=batch)

    def update_graphic(self):
        self.graphics.x = self.pos.x
        self.graphics.y = self.pos.y

    @property
    def velocity(self) -> Vector2D:
        return self.pos-self.old

    def __eq__(self, other: 'Boid') -> bool:
        return self.id == other.id

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(id={self.id},pos={self.pos},old={self.old})'

    def separation(self, boids: list['Boid']) -> Vector2D:
        displacement = Vector2D(0, 0)
        for boid in boids:
            if self.id != boid.id:
                if self.pos.euclidean_distance(boid.pos) < SEPARATION_DISTANCE:
                    displacement -= boid.pos - self.pos
        return displacement

    def alignment(self, boids: list['Boid']) -> Vector2D:
        velocity = Vector2D(0, 0)
        for boid in boids:
            if self.id != boid.id:
                velocity += boid.velocity
        velocity /= len(boids) - 1
        return velocity - self.velocity

    def cohesion(self, boids: list['Boid']) -> Vector2D:
        total = ORIGIN_2D
        for boid in boids:
            if self.id != boid.id:
                total += boid.pos

        center = total / (len(boids)-1)
        center = center.clamp_bounds(ORIGIN_2D, WINDOW_SIZE)
        vector = center - self.pos
        return vector

    def remain(self) -> Vector2D:
        v = Vector2D(0, 0)
        if self.pos.x < 0:
            v.x = 10
        elif self.pos.x > WINDOW_SIZE.x:
            v.x = -10
        if self.pos.y < 0:
            v.y = 10
        elif self.pos.y > WINDOW_SIZE.y:
            v.y = -10
        return v

    @staticmethod
    def limit(velocity: Vector2D) -> Vector2D:
        magnitude = velocity.magnitude()
        if magnitude > SPEED_LIMIT:
            return velocity * (SPEED_LIMIT / magnitude)
        return velocity

    def goal(self) -> Vector2D:
        return GOAL_POSITION - self.pos

    def move(self, boids: list['Boid']) -> None:
        boids = [boid for boid in boids if self.pos.euclidean_distance(
            boid.pos) < VIEW_DISTANCE]
        velocity = self.velocity
        if len(boids) > 1:
            velocity += self.separation(boids) * SEPARATION_FACTOR
            velocity += self.alignment(boids) * ALIGNMENT_FACTOR
            velocity += self.cohesion(boids) * COHESION_FACTOR
        velocity += self.remain() * REMAIN_FACTOR
        velocity += self.goal() * GOAL_FACTOR
        velocity += Vector2D.random(Point2D(-2, -2), Point2D(2, 2))
        velocity = Boid.limit(velocity)

        # self.old = self.pos
        self.pos += velocity
        self.pos %= WINDOW_SIZE
        self.old = self.pos - velocity
        self.update_graphic()
