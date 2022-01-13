from noise import pnoise2, snoise2
from random import randint
from numba import cuda
import numpy as np
import pyglet


GPU_BLOCKS = 20
GPU_THREADS_PER_BLOCK = 64
GPU_THREADS = GPU_THREADS_PER_BLOCK * GPU_BLOCKS

PIXEL_SIZE = (5,5)
WINDOW_SIZE = (1000,800)
SEED = randint(-10000,10000)
OCTAVES = 8
FREQ = 16.0 * OCTAVES
PIXEL_RANGE = (WINDOW_SIZE[0]//PIXEL_SIZE[0],WINDOW_SIZE[1]//PIXEL_SIZE[1])
PIXEL_COUNT = PIXEL_RANGE[0] * PIXEL_RANGE[1]
TERRAINS = {
    0:(35, 94, 113), #Deep Water
    105:(173, 216, 230), #Shallow Water
    118:(255, 240, 201), #Beach
    125:(0,127,0), #Grass
    135:(0,100,0), #Forest
    160:(120,120,120), #Low Mountain
    165:(150,150,150), #Mountain
    170:(250,250,250), #Snow
    255:(255,100,100) #Catch-all
}

offset = (0,0)
zoom_level = 1.0

window = pyglet.window.Window(width=WINDOW_SIZE[0],height=WINDOW_SIZE[1],resizable=False)
batch = pyglet.graphics.Batch()
cursor_text = pyglet.text.Label('',font_name='Courier',font_size=12,x=WINDOW_SIZE[0]//2,y=WINDOW_SIZE[1]//2,anchor_x='left',anchor_y='center',batch=batch,color=(0,0,0,255))

rects = []
for y in range(WINDOW_SIZE[1]//PIXEL_SIZE[1]):
    row = []
    for x in range(WINDOW_SIZE[0]//PIXEL_SIZE[0]):
        row.append(pyglet.shapes.Rectangle(x*PIXEL_SIZE[0],y*PIXEL_SIZE[1],PIXEL_SIZE[0],PIXEL_SIZE[1],(0,0,0),batch))
    rects.append(row)

@window.event
def on_draw():
    # window.clear()
    batch.draw()

@cuda.jit
def gpu_update(out):
    thread_id = cuda.grid(1)

    for y in range():
        for x in range():
            block = y * PIXEL_RANGE[0] + x

            #sample = DRAG_OFFSET + LOCATION_ON_SCREEN + ZOOM_TO_CENTER_OFFSET
            sample_x = offset[0]/FREQ + x/FREQ/zoom_level - (WINDOW_SIZE[0]//PIXEL_SIZE[0])/2/FREQ/zoom_level + SEED
            sample_y = offset[1]/FREQ + y/FREQ/zoom_level - (WINDOW_SIZE[1]//PIXEL_SIZE[1])/2/FREQ/zoom_level + SEED
            z = pnoise2(sample_x, sample_y, OCTAVES)
            z_scaled = int(z * 127.0 + 128.0)
            for t in TERRAINS:
                if z_scaled > t:
                    color = TERRAINS[t]
                else:
                    break
            rects[y][x].color = color

def update(_):
    out = np.zeros((PIXEL_COUNT,3), dtype=np.uint8)
    gpu_update[GPU_BLOCKS,GPU_THREADS_PER_BLOCK](out)
    

@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    global zoom_level,offset
    if zoom_level < 8 and scroll_y > 0:
        zoom_level *= 2
        # new_x = offset[0] + (x - WINDOW_SIZE[0]//2) // zoom_level // 2
        # new_y = offset[1] + (y - WINDOW_SIZE[1]//2) // zoom_level // 2
        # offset = (new_x,new_y)
    elif zoom_level > 0.125 and scroll_y < 0:
        zoom_level *= 1/2
        # new_x = offset[0] - (x - WINDOW_SIZE[0]//2) // zoom_level // 2
        # new_y = offset[1] - (y - WINDOW_SIZE[1]//2) // zoom_level // 2
        # offset = (new_x,new_y)


@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    global offset
    new_x = (offset[0]*zoom_level - dx * 0.2) / zoom_level
    new_y = (offset[1]*zoom_level - dy * 0.2) / zoom_level
    offset = (new_x,new_y)

    on_mouse_motion(x,y,dx,dy)

@window.event
def on_mouse_motion(x, y, dx, dy):
    cursor_text.x = x+5
    cursor_text.y = y
    cursor_text.text = f'({round(offset[0]*5+x)},{round(offset[1]*5+y)})'

if __name__ == '__main__':
	pyglet.clock.schedule_interval(update, 1/30)
	pyglet.app.run()