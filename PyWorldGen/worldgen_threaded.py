from threading import Thread
from random import randint
from noise import pnoise2
from debug import profile
import pyglet


THREADS = 1
OCTAVES = 8
FREQ = 16.0 * OCTAVES
SEED = randint(-10000,10000)

PIXEL_SIZE = (5,5)
WINDOW_SIZE = (1000,800)
PIXEL_RANGE = (WINDOW_SIZE[0]//PIXEL_SIZE[0],WINDOW_SIZE[1]//PIXEL_SIZE[1])
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
for y in range(PIXEL_RANGE[1]):
    row = []
    for x in range(PIXEL_RANGE[0]):
        row.append(pyglet.shapes.Rectangle(x*PIXEL_SIZE[0],y*PIXEL_SIZE[1],PIXEL_SIZE[0],PIXEL_SIZE[1],(0,0,0),batch))
    rects.append(row)

@window.event
def on_draw():
    # window.clear()
    batch.draw()

def thread_update(thread_id):
    for y in range(thread_id,PIXEL_RANGE[1],THREADS):
        for x in range(PIXEL_RANGE[0]):
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

@profile
def update_screen(_):
    global rects,offset
    threads = []
    for i in range(THREADS):
        t = Thread(target=thread_update,args=[i],name='t'+str(i))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    global zoom_level,offset
    if zoom_level < 8 and scroll_y > 0:
        zoom_level *= 2
    elif zoom_level > 0.125 and scroll_y < 0:
        zoom_level *= 1/2


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
	pyglet.clock.schedule_interval(update_screen, 1/60)
	pyglet.app.run()