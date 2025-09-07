import displayio
from adafruit_display_text import bitmap_label as label
import terminalio
import time

class WelcomePanel:
    def __init__(self, display):
        self.display = display

    def show(self, wifi=False, mqtt=False):
        splash = displayio.Group()
        self.display.root_group = splash

        width, height = 128, 128
        box_width = 100
        box_height = 50
        border = 2
        x = (width - box_width) // 2
        y = (height - box_height) // 2

        # Outer white border
        border_bitmap = displayio.Bitmap(box_width, box_height, 1)
        border_palette = displayio.Palette(1)
        border_palette[0] = 0xFFFFFF
        border_sprite = displayio.TileGrid(border_bitmap, pixel_shader=border_palette, x=x, y=y)
        splash.append(border_sprite)

        # Inner black box
        inner_bitmap = displayio.Bitmap(box_width - border*2, box_height - border*2, 1)
        inner_palette = displayio.Palette(1)
        inner_palette[0] = 0x000000
        inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=x+border, y=y+border)
        splash.append(inner_sprite)

        wifi_text = "Network (DONE)" if wifi else "Network (...)"
        # Wifi
        text_label = label.Label(terminalio.FONT, text=wifi_text, color=0xFFFFFF)
        text_label.anchor_point = (0.5, 0.5)
        text_label.anchored_position = (width//2, height//2-10)
        splash.append(text_label)
        
        # MQTT
        mqtt_text = "MQTT (DONE)" if mqtt else "MQTT (...)"
        text_label = label.Label(terminalio.FONT, text=mqtt_text, color=0xFFFFFF)
        text_label.anchor_point = (0.5, 0.5)
        text_label.anchored_position = (width//2, height//2)
        splash.append(text_label)
        
        if wifi and mqtt:
            done_label = label.Label(terminalio.FONT, text="All set!", color=0x00FF00)
            done_label.anchor_point = (0.5, 0.5)
            done_label.anchored_position = (width//2, height//2 + 15)
            splash.append(done_label)
            time.sleep(5)