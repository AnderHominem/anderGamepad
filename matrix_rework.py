import time
import board
import digitalio
import usb_hid

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse

# Initialize HID devices
keyboard = Keyboard(usb_hid.devices)
mouse = Mouse(usb_hid.devices)

# Define keypad matrix pins
keypad_rows = [board.D0, board.D1, board.D2, board.D3, board.D4]
keypad_columns = [board.D19, board.D20, board.D21, board.D22]

# Map key positions to HID actions
matrix_keys = [
    [Keycode.A, Keycode.B, Mouse.LEFT_BUTTON, Keycode.D],
    [Keycode.E, Keycode.F, Keycode.G, Keycode.H],
    [Keycode.I, Keycode.J, Keycode.K, Keycode.L],
    [Keycode.ONE, Mouse.RIGHT_BUTTON, Keycode.M, Keycode.N],
    [Keycode.O, Keycode.P, Keycode.Q, Keycode.R]
]

# Create lists to hold row and column pins
col_pins = []
row_pins = []

# Initialize row pins as outputs
for row_pin in keypad_rows:
    pin = digitalio.DigitalInOut(row_pin)
    pin.direction = digitalio.Direction.OUTPUT
    pin.value = False  # Set to low initially
    row_pins.append(pin)

# Initialize column pins as inputs with pull-down resistors
for col_pin in keypad_columns:
    pin = digitalio.DigitalInOut(col_pin)
    pin.direction = digitalio.Direction.INPUT
    pin.pull = digitalio.Pull.DOWN
    col_pins.append(pin)

# Dictionary to keep track of pressed keys
pressed_keys = {}

def scankeys():
    for row in range(len(row_pins)):
        # Set the current row to high
        row_pins[row].value = True

        for col in range(len(col_pins)):
            # Check if the column pin is high (key pressed)
            if col_pins[col].value:
                key_action = matrix_keys[row][col]
                if key_action not in pressed_keys:
                    # New key press
                    pressed_keys[key_action] = True
                    print("Key pressed:", key_action)
                    
                    if isinstance(key_action, int):  # Keycode
                        keyboard.press(key_action)
                    if key_action in [Mouse.LEFT_BUTTON, Mouse.RIGHT_BUTTON]:
                        mouse.press(key_action)

            else:
                # If the key was previously pressed, release it
                key_action = matrix_keys[row][col]
                if key_action in pressed_keys:
                    print("Key released:", key_action)
                    pressed_keys.pop(key_action)
                    
                    if isinstance(key_action, int):  # Keycode
                        keyboard.release(key_action)
                    if key_action in [Mouse.LEFT_BUTTON, Mouse.RIGHT_BUTTON]:
                        mouse.release(key_action)

        # Set the current row back to low
        row_pins[row].value = False

while True:
    scankeys()
    time.sleep(0.01)  # Small delay to reduce CPU usage
      
       