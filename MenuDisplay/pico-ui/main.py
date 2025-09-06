import board
import displayio
import busio
import digitalio
import rotaryio
import terminalio
from adafruit_display_text import bitmap_label as label
from adafruit_displayio_sh1107 import SH1107, DISPLAY_OFFSET_ADAFRUIT_128x128_OLED_5297
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.bitmap_label import Label

import time

from dishwasher import go_dishwasher
import constants

displayio.release_displays()
i2c = busio.I2C(scl=board.GP21, sda=board.GP20)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)

display = SH1107(
    display_bus,
    width=constants.WIDTH,
    height=constants.HEIGHT,
    display_offset=DISPLAY_OFFSET_ADAFRUIT_128x128_OLED_5297,
    rotation=constants.ROTATION,
)

encoder = rotaryio.IncrementalEncoder(board.GP27, board.GP26)

while encoder.position is None:
    time.sleep(0.01)
last_position = encoder.position

menu = [None] * 4  

menu[constants.DISHWASHER] = ('\uf1f7', "unload check-in", "Dishwasher")
menu[constants.WEATHER] = ('\ue2bd', "how is it today?", "Weather")
menu[constants.SENSORS] = ('\uEF3E', "hum,temp, air, etc", "Sensors")
menu[constants.SEND_DATA] = ('\ue85d', "send via email", "Send Data")

menu_index = 0

def draw_menu():
    # Make the display context
    splash = displayio.Group()
    display.root_group = splash

    color_bitmap = displayio.Bitmap(constants.WIDTH, constants.HEIGHT, 1)
    color_palette = displayio.Palette(1)
    color_palette[0] = 0xFFFFFF  # White

    bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
    splash.append(bg_sprite)

    # Draw a smaller inner rectangle in black
    inner_bitmap = displayio.Bitmap(constants.WIDTH - constants.BORDER * 2, constants.HEIGHT - constants.BORDER * 2, 1)
    inner_palette = displayio.Palette(1)
    inner_palette[0] = 0x000000  # Black
    inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=constants.BORDER, y=constants.BORDER)
    splash.append(inner_sprite)

    # Menu text label
    icons = bitmap_font.load_font("fonts/icons.bdf")
    icon_area = label.Label(font=icons, text=menu[menu_index][0], x=30, y=70)
    splash.append(icon_area)

    legend = label.Label(terminalio.FONT, text=menu[menu_index][1], scale=1, color=0xFFFFFF, x=10, y=110)
    splash.append(legend)

    menu_text_area = label.Label(terminalio.FONT, text=menu[menu_index][2], scale=2, color=0xFFFFFF, x=5, y=24)
    splash.append(menu_text_area)
    
    return icon_area, legend, menu_text_area

button = digitalio.DigitalInOut(board.GP22)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP  # Assumes button pulls pin LOW when pressed

icon_area, legend, menu_text_area = draw_menu()

while True:
    position = encoder.position
    if position != last_position:
        if position > last_position:
            menu_index = (menu_index + 1) % len(menu)
        else:
            menu_index = (menu_index - 1) % len(menu)
        last_position = position

        # Update icon and text
        icon_area.text = menu[menu_index][0]
        legend.text = menu[menu_index][1]
        menu_text_area.text = menu[menu_index][2]
    
    if not button.value: 
        if menu_index == constants.DISHWASHER:
            go_dishwasher(display, encoder, button)
        elif menu_index == constants.WEATHER:
            print("Weather selected")
        elif menu_index == constants.SENSORS:
            print("Sensors selected")
        elif menu_index == constants.SEND_DATA:
            print("Send Data selected")
                
        print("Button pressed! Action for:", menu[menu_index][2])
        icon_area, legend, menu_text_area = draw_menu()

        time.sleep(0.2)

    time.sleep(0.05)