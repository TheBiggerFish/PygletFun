from noise import pnoise2, snoise2
import pyglet
from random import randint, sample


SEED = randint(-10000,10000)
OCTAVES = 8
FREQ = 16.0 * OCTAVES
PIXEL_SIZE = (5,5)
WINDOW_SIZE = (1000,800)
PIXEL_RANGE = (WINDOW_SIZE[0]//PIXEL_SIZE[0],WINDOW_SIZE[1]//PIXEL_SIZE[1])
offset = (0,0)
zoom_level = 1.0
TERRAINS = {
    0:(35,94,113), #Deep Water
    108:(173,216,230), #Shallow Water
    117:(255,240,201), #Beach
    122:(0,127,0), #Grass
    135:(0,100,0), #Forest
    160:(120,120,120), #Low Mountain
    165:(150,150,150), #Mountain
    170:(250,250,250), #Snow
    255:(255,100,100) #Catch-all
}

window = pyglet.window.Window(width=WINDOW_SIZE[0],height=WINDOW_SIZE[1],resizable=False)
batch = pyglet.graphics.Batch()
cursor_text = pyglet.text.Label('',font_name='Courier',font_size=12,x=WINDOW_SIZE[0]//2,y=WINDOW_SIZE[1]//2,anchor_x='left',anchor_y='center',batch=batch,color=(0,0,0,255))
zoom_text = pyglet.text.Label('Zoom: 1x',font_name='Courier New',font_size=12,x=10,y=WINDOW_SIZE[1]-15,batch=batch,color=(0,0,0,255))
color_buffer = [[(0,0,0) for x in range(PIXEL_RANGE[0])] for y in range(PIXEL_RANGE[1])]

rects:list[list[pyglet.shapes.Rectangle]] = []
for y in range(WINDOW_SIZE[1]//PIXEL_SIZE[1]):
    row = []
    for x in range(WINDOW_SIZE[0]//PIXEL_SIZE[0]):
        row.append(pyglet.shapes.Rectangle(x*PIXEL_SIZE[0],y*PIXEL_SIZE[1],PIXEL_SIZE[0],PIXEL_SIZE[1],(0,0,0),batch=batch))
    rects.append(row)

@window.event
def on_draw():
    # window.clear()
    batch.draw()

def update(_):
    global rects,offset
    for y in range(WINDOW_SIZE[1]//PIXEL_SIZE[1]):
        for x in range(WINDOW_SIZE[0]//PIXEL_SIZE[0]):
            #sample = DRAG_OFFSET + LOCATION_ON_SCREEN + ZOOM_TO_CENTER_OFFSET
            x_centered = (x - (WINDOW_SIZE[0]//PIXEL_SIZE[0])/2)/zoom_level
            sample_x = offset[0] + x_centered + SEED
            sample_x /= FREQ

            y_centered = (y - (WINDOW_SIZE[1]//PIXEL_SIZE[1])/2)/zoom_level
            sample_y = offset[1] + y_centered + SEED
            sample_y /= FREQ

            z = pnoise2(sample_x, sample_y, OCTAVES)
            z_scaled = int(z * 127.0 + 128.0)
            for t in TERRAINS:
                if z_scaled > t:
                    color = TERRAINS[t]
                else:
                    break
            if color_buffer[y][x] != color:
                color_buffer[y][x] = color
                rects[y][x].color = color

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
    zoom_text.text = f'Zoom: {zoom_level}x'


@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    global offset
    new_x = (offset[0]*zoom_level - dx / PIXEL_SIZE[0]) / zoom_level
    new_y = (offset[1]*zoom_level - dy / PIXEL_SIZE[0]) / zoom_level
    offset = (new_x,new_y)

    on_mouse_motion(x,y,dx,dy)

@window.event
def on_mouse_motion(x, y, dx, dy):
    cursor_text.x = x+5
    cursor_text.y = y
    text_x = (offset[0] + x/zoom_level - (WINDOW_SIZE[0]//PIXEL_SIZE[0])/2/zoom_level + SEED)/FREQ
    text_y = (offset[1] + y/zoom_level - (WINDOW_SIZE[1]//PIXEL_SIZE[1])/2/zoom_level + SEED)/FREQ
    cursor_text.text = f'({round(text_x)},{round(text_y)})'

if __name__ == '__main__':
	pyglet.clock.schedule_interval(update, 1/60)
	pyglet.app.run()