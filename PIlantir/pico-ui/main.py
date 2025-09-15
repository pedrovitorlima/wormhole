import board
import displayio
import busio
import digitalio
import rotaryio
import terminalio
from adafruit_display_text import bitmap_label as label
from adafruit_displayio_sh1107 import SH1107, DISPLAY_OFFSET_ADAFRUIT_128x128_OLED_5297
from adafruit_bitmap_font import bitmap_font
from adafruit_minimqtt.adafruit_minimqtt import MQTT
import i2cdisplaybus

from welcome_panel import WelcomePanel
from mqtt_manager import MqttManager
from wifi_manager import WifiManager
from dishwasher import go_dishwasher
import constants
import time

def init() -> SH1107:
    displayio.release_displays()
    i2c = busio.I2C(scl=board.GP21, sda=board.GP20)
    display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=0x3C)

    display = SH1107(
        display_bus,
        width=constants.WIDTH,
        height=constants.HEIGHT,
        display_offset=DISPLAY_OFFSET_ADAFRUIT_128x128_OLED_5297,
        rotation=constants.ROTATION,
    )
    return display

def connect(display: SH1107) -> tuple[MqttManager, MQTT]:
    welcome = WelcomePanel(display)
    welcome.show()

    wifi_manager = WifiManager(display)

    connected = False
    retry_count = 0
    mqtt_manager = None
    while not connected and retry_count < 3:
        try:
            pool, ssl_connect = wifi_manager.connect()
            welcome.show(wifi=True)

            mqtt_manager = MqttManager(pool, ssl_connect)
            mqtt_client = mqtt_manager.create_mqtt_client()
            connected = True
            welcome.show(wifi=True, mqtt=True)
            return mqtt_manager, mqtt_client
        except Exception as e:
            print("Failed to connect to WiFi or MQTT. Trying again:", e)
            retry_count += 1

    if not connected:
        raise RuntimeError("Could not connect to WiFi or MQTT after 3 attempts.")

def encoder() -> rotaryio.IncrementalEncoder:
    encoder = rotaryio.IncrementalEncoder(board.GP27, board.GP26)

    # Avoid infinite loop if encoder never updates
    timeout_start = time.monotonic()
    while encoder.position is None and time.monotonic() - timeout_start < 5:
        time.sleep(0.01)
    return encoder

def draw_menu() -> tuple[label.Label, label.Label, label.Label]:
    splash = displayio.Group()
    display.root_group = splash

    color_bitmap = displayio.Bitmap(constants.WIDTH, constants.HEIGHT, 1)
    color_palette = displayio.Palette(1)
    color_palette[0] = 0xFFFFFF
    bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
    splash.append(bg_sprite)

    inner_bitmap = displayio.Bitmap(constants.WIDTH - constants.BORDER * 2, constants.HEIGHT - constants.BORDER * 2, 1)
    inner_palette = displayio.Palette(1)
    inner_palette[0] = 0x000000
    inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=constants.BORDER, y=constants.BORDER)
    splash.append(inner_sprite)

    icon_area = label.Label(font=icons_font, text=menu[menu_index][0], x=30, y=70)
    splash.append(icon_area)

    legend = label.Label(terminalio.FONT, text=menu[menu_index][1], scale=1, color=0xFFFFFF, x=10, y=110)
    splash.append(legend)

    menu_text_area = label.Label(terminalio.FONT, text=menu[menu_index][2], scale=2, color=0xFFFFFF, x=5, y=24)
    splash.append(menu_text_area)

    return icon_area, legend, menu_text_area

def move_menu(position: int, last_position: int, menu_index: int) -> int:
    if position > last_position:
        menu_index = (menu_index + 1) % len(menu)
    else:
        menu_index = (menu_index - 1) % len(menu)

    icon_area.text = menu[menu_index][0]
    legend.text = menu[menu_index][1]
    menu_text_area.text = menu[menu_index][2]
    return menu_index

def handle_button_pressed(menu_index: int):
    try:
        mqtt_client.loop()
    except Exception as e:
        print("MQTT loop error:", e)
        
    if menu_index == constants.DISHWASHER:
        go_dishwasher(display, encoder, button, mqtt_manager)
    elif menu_index == constants.WEATHER:
        print("Weather selected")
    elif menu_index == constants.SENSORS:
        print("Sensors selected")
    elif menu_index == constants.SEND_DATA:
        print("Send Data selected")

    print("Button pressed! Action for:", menu[menu_index][2])

display = init()
mqtt_manager, mqtt_client = connect(display)

encoder = encoder()
last_position = encoder.position or 0

menu = [None] * 4
menu[constants.DISHWASHER] = ('\uf1f7', "unload check-in", "Dishwasher")
menu[constants.WEATHER] = ('\ue2bd', "how is it today?", "Weather")
menu[constants.SENSORS] = ('\uEF3E', "hum,temp, air, etc", "Sensors")
menu[constants.SEND_DATA] = ('\ue85d', "send via email", "Send Data")

menu_index = 0

# Cache fonts
icons_font = bitmap_font.load_font("fonts/icons.bdf")

button = digitalio.DigitalInOut(board.GP22)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

icon_area, legend, menu_text_area = draw_menu()

try:
    while True:
        position = encoder.position
        if position != last_position:
            menu_index = move_menu(position, last_position, menu_index)
            last_position = position

        if not button.value:
            # TODO handle re-connection (wifi and mqtt)
            handle_button_pressed(menu_index)
            icon_area, legend, menu_text_area = draw_menu()
            encoder.position = last_position # reset position after returning, as the encoder is shared across menus
            time.sleep(0.2)

        time.sleep(0.05)
except KeyboardInterrupt:
    print("Exiting and disconnecting from mqtt...")
    