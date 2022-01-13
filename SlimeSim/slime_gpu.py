import math
import random

import numpy as np
import pyglet
from fishpy.utility.debug import profile
from numba import cuda

SIMULATION_RATE = 50

SLIMES = 6000
SLIME_SIZE = 2.5
SLIME_COLOR = (173,216,230)
SLIME_SPEED = 3

GPU_BLOCKS = 96
GPU_BLOCKS_SHAPE = (8,12)
GPU_THREADS_PER_BLOCK = 64
GPU_THREADS_SHAPE = (8,8)
GPU_THREADS = GPU_THREADS_PER_BLOCK * GPU_BLOCKS
GPU_THREADS_X = (GPU_BLOCKS_SHAPE[0]*GPU_THREADS_SHAPE[0])
GPU_THREADS_Y = (GPU_BLOCKS_SHAPE[1]*GPU_THREADS_SHAPE[1])

INITIAL_DIRECTION_RANDOM = False
INITIAL_POSITION_RANDOM = False

WALL_BOUNCE_RANDOM_ANGLE = True
RANDOM_DIRECTION_CHANGE_CHANCE = 0.1

DISPERSAL_ENABLED = True
DEGRADATION_STEEPNESS = 1.44
DEGRADATION_OFFSET = 1.07

SENSOR_ANGLE = math.pi/4
SENSOR_OFFSET = 30
ROTATION_ANGLE = math.pi/4

PIXEL_SIZE = (4,4)
WINDOW_SIZE = (500,500)
PIXEL_COUNTS = (WINDOW_SIZE[0]//PIXEL_SIZE[0],WINDOW_SIZE[1]//PIXEL_SIZE[1])

window = pyglet.window.Window(width=WINDOW_SIZE[0],height=WINDOW_SIZE[1],resizable=False)
batch = pyglet.graphics.Batch()
opacity_buffer = np.zeros(PIXEL_COUNTS[0]*PIXEL_COUNTS[1])
pixels = []
slimes = []

for y in range(PIXEL_COUNTS[1]):
    row = []
    for x in range(PIXEL_COUNTS[0]):
        row.append(pyglet.shapes.Rectangle(x*PIXEL_SIZE[0],y*PIXEL_SIZE[1],PIXEL_SIZE[0],PIXEL_SIZE[1],SLIME_COLOR,batch=batch))
        row[-1].opacity = opacity_buffer[y*PIXEL_COUNTS[0]+x]
    pixels.append(row)


for s in range(SLIMES):
    x = random.randint(0,WINDOW_SIZE[0]-1) if INITIAL_POSITION_RANDOM else WINDOW_SIZE[0]//2
    y = random.randint(0,WINDOW_SIZE[1]-1) if INITIAL_POSITION_RANDOM else WINDOW_SIZE[1]//2
    theta = random.uniform(0,2*math.pi) if INITIAL_DIRECTION_RANDOM else s/SLIMES*2*math.pi
    slimes.append((x,y,theta))


def assess_square(x,y,theta):
    dx,dy = math.cos(theta),math.sin(theta)
    window_x,window_y = x+dx*SENSOR_OFFSET,y+dy*SENSOR_OFFSET
    pixel_x,pixel_y = int(window_x//PIXEL_SIZE[0]),int(window_y//PIXEL_SIZE[1])

    pixel_bounded_x = 0 if pixel_x < 0 else PIXEL_COUNTS[0]-1 if pixel_x > PIXEL_COUNTS[0]-1 else pixel_x
    pixel_bounded_y = 0 if pixel_y < 0 else PIXEL_COUNTS[1]-1 if pixel_y > PIXEL_COUNTS[1]-1 else pixel_y
    return opacity_buffer[pixel_bounded_y*PIXEL_COUNTS[0]+pixel_bounded_x]


def follow_trail(slime):
    x,y,theta = slime[0],slime[1],slime[2]

    forward = assess_square(x,y,theta)
    left = assess_square(x,y,theta+SENSOR_ANGLE)
    right = assess_square(x,y,theta-SENSOR_ANGLE)

    if forward > left and forward > right:
        return 0
    elif forward < left and forward < right and (left != 0 and right != 0):
        return (random.randint(0,1)*2-1) * ROTATION_ANGLE
    elif left > right:
        return ROTATION_ANGLE
    elif right > left:
        return -ROTATION_ANGLE
    else:
        return 0
    
    
def update_slime(slime):
    x,y,theta = slime[0],slime[1],slime[2]
    dx,dy = SLIME_SPEED*math.cos(theta),SLIME_SPEED*math.sin(theta)
    reflect_x,reflect_y = False,False

    if x+dx > WINDOW_SIZE[0] and dx > 0:
        dx = -dx
        reflect_x = True
    elif x+dx < 0 and dx < 0:
        dx = -dx
        reflect_x = True
    if y+dy > WINDOW_SIZE[1] and dy > 0:
        dy = -dy
        reflect_y = True
    elif y+dy < 0 and dy < 0:
        dy = -dy
        reflect_y = True

    if reflect_x:
        if WALL_BOUNCE_RANDOM_ANGLE:
            theta = random.uniform(0,2*math.pi)
        else:
            theta = (3*math.pi - theta) % (2*math.pi)
    elif reflect_y:
        if WALL_BOUNCE_RANDOM_ANGLE:
            theta = random.uniform(0,2*math.pi)
        else:
            theta = math.pi*2 - theta
    else:
        if random.random() < RANDOM_DIRECTION_CHANGE_CHANCE:
            theta += random.uniform(-math.pi/4,math.pi/4)
        else:
            theta += follow_trail(slime)
        theta %= 2*math.pi

    x,y = x+dx,y+dy
    return (x,y,theta)

def update(_):
    slimes_pos = np.array(slimes).flatten()
    opacity_out = np.zeros(len(opacity_buffer))
    draw[GPU_BLOCKS_SHAPE,GPU_THREADS_SHAPE](opacity_buffer, slimes_pos, opacity_out)

    for i in range(len(slimes)):
        slimes[i] = update_slime(slimes[i])
    

    for x in range(PIXEL_COUNTS[0]):
        for y in range(PIXEL_COUNTS[1]):
            i = y*PIXEL_COUNTS[0]+x
            out = opacity_out[i]
            if opacity_buffer[i] != out:
                opacity_buffer[i] = out
                pixels[y][x].opacity = out
    window.clear()
    batch.draw()

@cuda.jit
def draw(opacity_in, slimes_pos, opacity_out):
    thread_id = cuda.grid(2)

    min_pixel_x = int(thread_id[0]*PIXEL_COUNTS[0]/GPU_THREADS_X)
    max_pixel_x = int((thread_id[0]+1)*PIXEL_COUNTS[0]/GPU_THREADS_X)
    min_pixel_y = int(thread_id[1]*PIXEL_COUNTS[1]/GPU_THREADS_Y)
    max_pixel_y = int((thread_id[1]+1)*PIXEL_COUNTS[1]/GPU_THREADS_Y)

    min_pos_x = min_pixel_x*PIXEL_SIZE[0]
    max_pos_x = max_pixel_x*PIXEL_SIZE[0]
    min_pos_y = min_pixel_y*PIXEL_SIZE[1]
    max_pos_y = max_pixel_y*PIXEL_SIZE[1]

    for y in range(min_pixel_y,max_pixel_y):
        for x in range(min_pixel_x,max_pixel_x):
            if DISPERSAL_ENABLED:
                opacity,count = 0,0
                for dis_x in range(x-1 if x > 0 else 0, x+2 if x < PIXEL_COUNTS[0]-1 else PIXEL_COUNTS[0]-1):
                    for dis_y in range(y-1 if y > 0 else 0, y+2 if y < PIXEL_COUNTS[1]-1 else PIXEL_COUNTS[1]-1):
                        opacity += opacity_in[dis_y*PIXEL_COUNTS[0]+dis_x]
                        count += 1
                opacity /= count
            else:
                opacity = opacity_in[y*PIXEL_COUNTS[0]+x]
                
            if opacity < 5:
                opacity_out[y*PIXEL_COUNTS[0]+x] = 0
            else:
                opacity = opacity/255
                opacity = (opacity ** DEGRADATION_STEEPNESS / (opacity ** DEGRADATION_STEEPNESS + (DEGRADATION_OFFSET * (1-opacity)) ** DEGRADATION_STEEPNESS))
                opacity_out[y*PIXEL_COUNTS[0]+x] = int(255 * 0.9 * opacity)

    for i in range(0,len(slimes_pos),3):
        x,y = slimes_pos[i],slimes_pos[i+1]
        if min_pos_x <= x < max_pos_x and min_pos_y <= y < max_pos_y:
            pixel_x,pixel_y = int(x/PIXEL_SIZE[0]),int(y/PIXEL_SIZE[1])
            opacity_out[pixel_y*PIXEL_COUNTS[0]+pixel_x] = 255

# @window.event
# def on_mouse_drag(x,y,dx,dy,buttons,modifiers):
#     pixel_x,pixel_y = int(x//PIXEL_SIZE[0]),int(y//PIXEL_SIZE[1])
#     opacity_buffer[pixel_y*PIXEL_COUNTS[0]+pixel_x] = 255

    
if __name__ == '__main__':
    pyglet.clock.schedule_interval(update, 1/SIMULATION_RATE)
    pyglet.app.run()
