import time
import board
import digitalio
import usb_hid
import analogio

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse

# Initialize HID devices
keyboard = Keyboard(usb_hid.devices)
mouse = Mouse(usb_hid.devices)
joysticks = Keyboard(usb_hid.devices)

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
        row_pins[row].value = True   # Set the current row to high

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

#___________________Rotary Encoder Function______________________
# Define GPIO pins for the rotary encoder
CLK_PIN = board.D6
DT_PIN = board.D7
SW_PIN = board.D5

# Set up the rotary encoder pins
clk = digitalio.DigitalInOut(CLK_PIN)
clk.direction = digitalio.Direction.INPUT
clk.pull = digitalio.Pull.UP  # Pull-up resistor

dt = digitalio.DigitalInOut(DT_PIN)
dt.direction = digitalio.Direction.INPUT
dt.pull = digitalio.Pull.UP  # Pull-up resistor

# Set up the switch pin
sw = digitalio.DigitalInOut(SW_PIN)
sw.direction = digitalio.Direction.INPUT
sw.pull = digitalio.Pull.UP  # Pull-up resistor

# Initialize variables
previous_clk_value = clk.value
counter = 0

#___________________Joystiks Function______________________

DEFAULT_UP = 26536
DEFAULT_DOWN = 39000

ACTIVE_UP = 15536
ACTIVE_DOWN = 50000

# Helper function to read joystick axis value
def read_axis(axis):
    return axis.value
#_____________________Left joystick________________________

# Joystick pins
left_y_axis = analogio.AnalogIn(board.A0)  # X-axis potentiometer pin
left_x_axis = analogio.AnalogIn(board.A1)  # Y-axis potentiometer pin

l_up_action = (Keycode.W)
l_down_action = (Keycode.S)
l_right_action = (Keycode.D)
l_left_action = (Keycode.A)

#_____________________Right joystick________________________

# Joystick pins
right_y_axis = analogio.AnalogIn(board.A2)  # X-axis potentiometer pin
right_x_axis = analogio.AnalogIn(board.A3)  # Y-axis potentiometer pin

r_up_action = (Keycode.UP_ARROW)
r_down_action = (Keycode.DOWN_ARROW)
r_right_action = (Keycode.RIGHT_ARROW)
r_left_action = (Keycode.LEFT_ARROW)

#___________________Working State______________________
while True:
    
#___________________Keypad Matrix Function______________________
    scankeys()
    time.sleep(0.01)  # Small delay to reduce CPU usage
#___________________Rotary Encoder Function______________________
    # Read the current state of the CLK pin
    current_clk_value = clk.value

    # Check if the encoder is turned
    if current_clk_value != previous_clk_value:
        if current_clk_value == 0:  # Clockwise turn
            if dt.value == 0:  # If DT is low, it's a clockwise turn
                counter += 1
                mouse.move(wheel=10)
            else:  # If DT is high, it's a counterclockwise turn
                counter -= 1
                mouse.move(wheel=-10)
                       
        # Update previous CLK value
        previous_clk_value = current_clk_value

    # Check if the switch is pressed
    if not sw.value:  # Switch is pressed
        mouse.click(Mouse.MIDDLE_BUTTON)
        time.sleep(0.25)  # Debounce delay

#___________________Joystiks Function______________________
#_____________________Left joystick________________________    

    l_x_value = read_axis(left_x_axis)
    l_y_value = read_axis(left_y_axis)

# Reset key states
    l_joystick_key_pressed = set()

# Detect Y-axis movement (W and S keys)
    if l_y_value <= ACTIVE_UP:
        l_joystick_key_pressed.add(l_right_action)  # Add W key for "up"  
    elif l_y_value >= DEFAULT_UP:
        joysticks.release(l_right_action)
    
    if l_y_value >= ACTIVE_DOWN:
        l_joystick_key_pressed.add(l_left_action)  # Add S key for "down"
    elif l_y_value <= DEFAULT_DOWN:
        joysticks.release(l_left_action)

# Detect X-axis movement (A and D keys)
    if l_x_value <= ACTIVE_UP:
        l_joystick_key_pressed.add(l_up_action)  # Add A key for "left"
    elif l_x_value >= DEFAULT_UP:
        joysticks.release(l_up_action)
    
    if l_x_value >= ACTIVE_DOWN:
        l_joystick_key_pressed.add(l_down_action)  # Add D key for "right"
    elif l_x_value <= DEFAULT_DOWN:
        joysticks.release(l_down_action)

# Press the keys currently in the `pressed_keys` set
    for key in l_joystick_key_pressed:
        joysticks.press(key)

#_____________________Right joystick________________________    


    r_x_value = read_axis(right_x_axis)
    r_y_value = read_axis(right_y_axis)

# Reset key states
    r_joystick_key_pressed = set()

# Detect Y-axis movement (W and S keys)
    if r_y_value <= ACTIVE_UP:
        r_joystick_key_pressed.add(r_right_action)  # Add W key for "up"  
    elif r_y_value >= DEFAULT_UP:
        joysticks.release(r_right_action)
    
    if r_y_value >= ACTIVE_DOWN:
        r_joystick_key_pressed.add(r_left_action)  # Add S key for "down"
    elif r_y_value <= DEFAULT_DOWN:
        joysticks.release(r_left_action)

# Detect X-axis movement (A and D keys)
    if r_x_value <= ACTIVE_UP:
        r_joystick_key_pressed.add(r_down_action)  # Add A key for "left"
    elif r_x_value >= DEFAULT_UP:
        joysticks.release(r_down_action)
    
    if r_x_value >= ACTIVE_DOWN:
        r_joystick_key_pressed.add(r_up_action)  # Add D key for "right"
    elif r_x_value <= DEFAULT_DOWN:
        joysticks.release(r_up_action)

# Press the keys currently in the `pressed_keys` set
    for key in r_joystick_key_pressed:
        joysticks.press(key)
    
    time.sleep(0.01)  # Small delay to reduce CPU usage
