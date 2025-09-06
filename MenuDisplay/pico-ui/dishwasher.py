import displayio
import constants
import time
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.bitmap_label import Label

def select_user(option, x, y):
    offset_x = 0
    offset_y = 30
    
    if option != 1:
        offset_x = 60
        
    line_width = 50  
    line_height = 3  
    line_x = x + offset_x
    line_y = y + offset_y 

    line_bitmap = displayio.Bitmap(line_width, line_height, 2)
    line_palette = displayio.Palette(2)
    line_palette[0] = 0x000000  
    line_palette[1] = 0xFFFFFF  

    for x in range(line_width):
        for y in range(line_height):
            line_bitmap[x, y] = 1

    line_sprite = displayio.TileGrid(line_bitmap, pixel_shader=line_palette, x=line_x, y=line_y)
    return line_sprite
    
# display is a SH1107
def go_dishwasher(display, encoder, button):
    option = 0
    last_position = encoder.position
    
    blank_group = displayio.Group()
    # Create a black bitmap covering the whole screen
    black_bitmap = displayio.Bitmap(constants.WIDTH, constants.HEIGHT, 1)
    black_palette = displayio.Palette(1)
    black_palette[0] = 0x000000  # Black
    black_sprite = displayio.TileGrid(black_bitmap, pixel_shader=black_palette, x=0, y=0)
    blank_group.append(black_sprite)

    # Load the icon font
    icons_font = bitmap_font.load_font("fonts/icons_small.bdf")

    # Display two icons
    man_icon = Label(icons_font, text="\uE87C", color=0xFFFFFF, x=10, y=64)
    woman_icon = Label(icons_font, text="\uf8db", color=0xFFFFFF, x=75, y=64)
    blank_group.append(man_icon)
    blank_group.append(woman_icon)
    
    blank_group.append(select_user(option=2, x=man_icon.x, y=man_icon.y))

    display.root_group = blank_group

    while not button.value:
        time.sleep(0.01)
        
    while True:
        position = encoder.position
        if position != last_position:

            option = 1 if option == 0 else 0
            last_position = position

            blank_group.pop()
            select_line = select_user(option=option, x=man_icon.x, y=man_icon.y)
            blank_group.append(select_line)


        if not button.value:
            break

        time.sleep(0.05)