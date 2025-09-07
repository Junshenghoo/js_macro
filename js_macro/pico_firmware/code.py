import board
import digitalio
import busio
import usb_hid
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.type_string import type_string
import busio
import displayio
from adafruit_display_text import label
from adafruit_displayio_ssd1306 import SSD1306
import terminalio
import json
import time

prototype = 0

displayio.release_displays()

def setup_display():
    # Set up I2C and the display
    i2c = busio.I2C(scl=board.GP21, sda=board.GP20)
    display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)

    WIDTH = 128
    HEIGHT = 64
    display = SSD1306(display_bus, width=WIDTH, height=HEIGHT)
    return display

def display_img():
    with open("display.json", "r") as file:
        data = json.load(file)
        bitmap_data = data["bitmap_data"]

    height = len(bitmap_data)
    width = len(bitmap_data[0])

    bitmap = displayio.Bitmap(width, height, 2)   # 2 colors
    palette = displayio.Palette(2)
    palette[0] = 0x000000   # black
    palette[1] = 0xFFFFFF   # white

    # Copy data into bitmap
    for y in range(height):
        for x in range(width):
            bitmap[x, y] = bitmap_data[y][x]

    # Show it (center if smaller than screen)
    tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette, x=64-width//2, y=32-height//2)

    group = displayio.Group()
    group.append(tile_grid)
    display.root_group = group

def display_words(mode_text, button_text, display):
    splash = displayio.Group()

    line1 = label.Label(terminalio.FONT, text=mode_text, x=10, y=5)
    line2 = label.Label(terminalio.FONT, text=button_text, x=10, y=30)

    splash.append(line1)
    splash.append(line2)

    display.root_group = splash

def display_start_up(text, display):
    # Create a display group and a text label
    splash = displayio.Group()
    text = label.Label(terminalio.FONT, text=text, x=10, y=30)
    splash.append(text)

    # Show it
    display.root_group = splash
    
def setup_button():
    # Define GPIO pins for each button
    if prototype:
        button_pins = [board.GP0, board.GP1, board.GP2, board.GP3, board.GP4,
                    board.GP5, board.GP6, board.GP7, board.GP8, board.GP9]
    else:
        button_pins = [board.GP8, board.GP17, board.GP16, board.GP15, board.GP14,
                   board.GP13, board.GP12, board.GP11, board.GP10, board.GP9]
    buttons = []

    # Set up each button
    for pin in button_pins:
        btn = digitalio.DigitalInOut(pin)
        btn.direction = digitalio.Direction.INPUT
        btn.pull = digitalio.Pull.DOWN
        buttons.append(btn)

    # Debounce tracker to avoid repeat key spam
    last_state = [False] * len(buttons)
    kbd = Keyboard(usb_hid.devices)
    layout = KeyboardLayoutUS(kbd)
    
    return last_state, buttons, kbd, layout

def pretty_print_json(obj, indent=0):
    for key, value in obj.items():
        print("  " * indent + f"{key}:")
        for item in value:
            for sub_key, sub_value in item.items():
                print("  " * (indent + 1) + f"{sub_key}: {sub_value}")
    print()  # Add an empty line after each block
    
def read_config(mode):
    with open("config.json", "r") as file:
        data = json.load(file)

    mode_key = f"mode{mode}"
    mode_data = data[mode_key]

    # Get the name
    mode_name = mode_data.get("name", f"Mode {mode}")

    # Convert list of key entries into a dict
    key_data = {}
    for key_entry in mode_data["keys"]:
        for key_name, actions in key_entry.items():
            key_data[key_name] = actions

    return mode_name, key_data

def execute_key(key_data, kbd, i):
    display_words(f"Mode: {mode_name}", f"Button {i}", display)
    key_name = f"key_{i}"
    print(key_name)
    
    if key_name not in key_data:
        print(f"No data for {key_name}, ignoring.")
        return

    for data in key_data[key_name]:
        if "cmd" in data:
            key_list = []
            for item in data["cmd"]:
                keycode = KEYCODE_MAP.get(item)
                if keycode:
                    key_list.append(keycode)
            #print(key_list)
            kbd.send(*key_list)
            time.sleep(0.01)
        elif "str" in data:
            layout.write(str(data["str"]))  # Type whole string at once
            time.sleep(0.01)

def load_keycode_map(filepath):
    with open(filepath, "r") as file:
        raw_map = json.load(file)
    # Convert string values to actual Keycode attributes
    return {k: getattr(Keycode, v) for k, v in raw_map.items()}

def get_max_mode():
    with open("config.json", "r") as file:
        data = json.load(file)
    mode_keys = [k for k in data.keys() if k.startswith("mode") and k[4:].isdigit()]
    max_mode = max([int(k[4:]) for k in mode_keys])
    return max_mode

last_state, buttons, kbd, layout = setup_button()
display = setup_display()
#display_start_up("Macro Keyboard", display)
display_img()
mode = 1
time.sleep(1)
mode_name, key_data = read_config(mode)
display_words(f"Mode: {mode_name}", f"Button {0}", display)
pretty_print_json(key_data)
KEYCODE_MAP = load_keycode_map("keycode_map_config.json")
time_counter = 0  

while True:
    time_counter += 1
    max_mode = get_max_mode()
    for i, button in enumerate(buttons):
        if button.value and not last_state[i]:
            if i == 0:
                mode += 1
                if mode == max_mode + 1:
                    mode = 1
                mode_name, key_data = read_config(mode)
                #pretty_print_json(key_data)
                display_words(f"Mode: {mode_name}", f"Button {i}", display)
            else:
                execute_key(key_data, kbd, i)

            last_state[i] = True
            time_counter = 0
        elif not button.value and last_state[i]:
            last_state[i] = False 
            time_counter = 0

    if time_counter == 100:
        display_img()
    time.sleep(0.01)