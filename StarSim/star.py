from fishpy.geometry.d2 import Point2D,Vector2D,Triangle,ORIGIN
from pyglet.shapes import Circle,Batch
from pyglet.gl import GL_TRIANGLES,GL_TRIANGLE_FAN
import random
import math

a = 0.5
b = 100
def transform(x:float):
    return x**a/(x**a + (1-x)**a)

class Star:
    WHITE = (255,255,255)
    YELLOW = (255,255,0)
    MAX_BRIGHTNESS = 100

    def __init__(self,size:int,color:tuple,pos:Point2D,brightness:float,twinkle_rate:float):
        self.size = size
        self.color = color
        self.pos = pos
        self.brightness = brightness
        self.twinkle_rate = twinkle_rate

    @staticmethod
    def random_star(bounds:Point2D,batch:Batch):
        size = 3*transform(random.uniform(0.1,1))
        pos = Point2D.random(Point2D(0,0),bounds-Point2D(1,1))
        brightness = random.randrange(10,Star.MAX_BRIGHTNESS)
        
        if random.randint(0,10) > 0:
            color = (255,255,random.randint(0,255))
        else:
            color = (150,150,random.randint(200,255))

        twinkle_rate = random.random()*2.5
        
        return Star(size,color,pos,brightness,twinkle_rate).set_graphics_object(batch)

    def set_graphics_object(self,batch:Batch):
        color = tuple(int(c*self.brightness/Star.MAX_BRIGHTNESS) for c in self.color)
        self.shape = Circle(self.pos.x,self.pos.y,self.size,color=color,batch=batch)
        return self

    def twinkle(self):
        self.brightness += self.twinkle_rate

        if self.brightness < 10:
            self.twinkle_rate = -self.twinkle_rate
            self.brightness = 20 - self.brightness
        elif self.brightness > Star.MAX_BRIGHTNESS:
            self.twinkle_rate = -self.twinkle_rate
            self.brightness = 2*Star.MAX_BRIGHTNESS - self.brightness

        self.shape.color = (c*self.brightness/Star.MAX_BRIGHTNESS for c in self.color)


class StarShape:
    def __init__(self,pos:Point2D,points:int,inner_radius:float,outer_radius:float,rotation:float,color:tuple,batch:Batch):
        self.pos = pos
        self.color = color
        self.points = points
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.rotation = rotation

        self.outline_points = []
        for i in range(points*2):
            angle = (rotation + (i/points)*math.pi) % (2*math.pi)
            if i % 2 == 0:
                self.outline_points.append(pos + Vector2D.from_vel(angle,inner_radius))
            else:
                self.outline_points.append(pos + Vector2D.from_vel(angle,outer_radius))

        for pt in self.outline_points:
            print(pt)

        # vertices = [item for pt in self.outline_points for item in pt.as_tuple()] + list(self.outline_points[0].as_tuple())
        triangles = []
        for i in range(0,len(self.outline_points),2):
            t = Triangle(self.outline_points[i],self.outline_points[i+1],self.outline_points[(i+2)%(points*2)])
            triangles += list(t.as_tuple())
        self.v_list_tips = batch.add(self.points*3,GL_TRIANGLES,None,('v2f',triangles),('c3B',self.color*(self.points*3)))

        center = [pos.x,pos.y]
        for i in range(0,len(self.outline_points)+2,2):
            center += [self.outline_points[i%len(self.outline_points)].x,self.outline_points[i%len(self.outline_points)].y]
        self.v_list_center = batch.add(self.points+2,GL_TRIANGLE_FAN,None,('v2f',center),('c3B',self.color*(self.points+2)))