import displayio
import constants
import time
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.bitmap_label import Label
import mqtt_manager

def select_user(option: int, x: int, y: int) -> displayio.TileGrid:
    # horizontal line below icon (selection highlight)
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

    for col in range(line_width):
        for row in range(line_height):
            line_bitmap[col, row] = 1

    return displayio.TileGrid(line_bitmap, pixel_shader=line_palette, x=line_x, y=line_y)

def draw_last_checkin(man_icon, woman_icon):
    icons_small_font = bitmap_font.load_font("fonts/icons_x_small.bdf")
    
    print(mqtt_manager.dishwasher.get("next"))
    if mqtt_manager.dishwasher.get("next", "man") == "woman":
        return Label(icons_small_font, text="\uE86C", color=0xFFFFFF, x=man_icon.x + man_icon.x // 2 + 8, y=man_icon.y // 2) 
    else:
        return Label(icons_small_font, text="\uE86C", color=0xFFFFFF, x=woman_icon.x + man_icon.x // 2 + 8, y=woman_icon.y // 2)
    
# display is a SH1107
def go_dishwasher(display, encoder, button, mqtt):
    option = 0
    last_position = encoder.position

    blank_group = displayio.Group()
    black_bitmap = displayio.Bitmap(constants.WIDTH, constants.HEIGHT, 1)
    black_palette = displayio.Palette(1)
    black_palette[0] = 0x000000
    blank_group.append(displayio.TileGrid(black_bitmap, pixel_shader=black_palette, x=0, y=0))

    icons_font = bitmap_font.load_font("fonts/icons_small.bdf")
    man_icon = Label(icons_font, text="\ue87c", color=0xFFFFFF, x=10, y=64)
    woman_icon = Label(icons_font, text="\uf8db", color=0xFFFFFF, x=75, y=64)
    blank_group.append(man_icon)
    blank_group.append(woman_icon)

    # horizontal line highlight
    select_line = select_user(option=option, x=man_icon.x, y=man_icon.y)
    blank_group.append(select_line)
    
    blank_group.append(draw_last_checkin(man_icon, woman_icon))
    
    display.root_group = blank_group

    while not button.value:
        time.sleep(0.01)

    while True:
        position = encoder.position
        if position != last_position:
            option = 1 if option == 0 else 0
            last_position = position

            blank_group.remove(select_line)
            select_line = select_user(option=option, x=man_icon.x, y=man_icon.y)
            blank_group.append(select_line)

        if not button.value:
            mqtt.update_dishwasher({"next": "man" if option == 0 else "woman"})
            break

        time.sleep(0.05)
