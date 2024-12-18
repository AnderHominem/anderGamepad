import time
import board
import digitalio
import usb_hid
import analogio
import busio
import adafruit_adxl34x
import pwmio


from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse

# Initialize HID devices
keyboard = Keyboard(usb_hid.devices)
mouse = Mouse(usb_hid.devices)
#joysticks = Keyboard(usb_hid.devices)

#___________________LED Controll______________________


# Define the RGB LED pins
RED_PIN = board.D15
GREEN_PIN = board.D14
BLUE_PIN = board.D13

# Set up PWM for each pin (0-65535 duty cycle)
red = pwmio.PWMOut(RED_PIN, frequency=1000, duty_cycle=0)
green = pwmio.PWMOut(GREEN_PIN, frequency=1000, duty_cycle=0)
blue = pwmio.PWMOut(BLUE_PIN, frequency=1000, duty_cycle=0)

def set_color(r, g, b):
    #Set the RGB LED color with PWM values (0-65535)
    red.duty_cycle = r
    green.duty_cycle = g
    blue.duty_cycle = b
# Define a default LED color (e.g., white: R=255, G=255, B=255)
DEFAULT_COLOR = (0, 0, 8000)
   
# Define keypad matrix pins
keypad_rows = [board.D0, board.D1, board.D2, board.D3, board.D4]
keypad_columns = [board.D19, board.D20, board.D21, board.D22]

# Map key positions to HID actions
matrix_keys = [
    [Keycode.F, Keycode.ONE, Mouse.RIGHT_BUTTON, Keycode.Z],
    [Keycode.TAB, Keycode.TWO, Keycode.G, Keycode.F6],
    [Keycode.FIVE, Keycode.THREE, Keycode.K, Keycode.F5],
    [Keycode.LEFT_CONTROL, Mouse.LEFT_BUTTON, Keycode.X, Keycode.ENTER],
    [Keycode.R, Keycode.FOUR, Keycode.Q, Keycode.T]
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
# Variable to track if Keycode.K is pressed
GAY_button = Keycode.K
mouse_movement_active = False

#flag to track if the LED color is already changed
button_pressed = False

# List of keys that should not send keypresses
ignored_keys = {Keycode.K}


def scankeys():
    
    global button_pressed, mouse_movement_active
    
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
                    
                    # Check if Keycode.K is pressed
                    if key_action == GAY_button:
                        mouse_movement_active = True
                        print("giro activated")
                        
                    # Skip ignored keys
                    if key_action in ignored_keys:
                        continue
                                         
                    if isinstance(key_action, int):  # Keycode
                        keyboard.press(key_action)
                                            
                        if key_action == Keycode.G:
                            button_pressed = True
                            set_color(42768, 3000, 0)                    
                        
                    if key_action in [Mouse.LEFT_BUTTON, Mouse.RIGHT_BUTTON]:
                        mouse.press(key_action)
                        if key_action == Mouse.LEFT_BUTTON:
                            button_pressed = True
                            set_color(32768, 0, 0)
                        if key_action == Mouse.RIGHT_BUTTON:
                            button_pressed = True
                            set_color(0, 32768, 0)
                            
                        
                    #if key_action in [Mouse.LEFT_BUTTON, Mouse.RIGHT_BUTTON]:
                        #mouse.press(key_action)

            else:
                # If the key was previously pressed, release it
                key_action = matrix_keys[row][col]
                if key_action in pressed_keys:
                    print("Key released:", key_action)
                    pressed_keys.pop(key_action)
                                                           
                    # Check if Keycode.K is released
                    if key_action == GAY_button:
                        mouse_movement_active = False
                        print("giro disactivated")
                        
                    # Skip ignored keys
                    if key_action in ignored_keys:
                        continue
                    
                    if isinstance(key_action, int):  # Keycode
                        keyboard.release(key_action)
                        button_pressed = False
                        
                    if key_action in [Mouse.LEFT_BUTTON, Mouse.RIGHT_BUTTON]:
                        mouse.release(key_action)
                        button_pressed = False
                        
                            

        # Set the current row back to low
        row_pins[row].value = False


#___________________Rotary Encoder Function______________________
# Initialize the rotary encoder pins
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

# Debounce delay in seconds
DEBOUNCE_DELAY = 0.01
last_clk_time = time.monotonic()

# Minimum signal duration in seconds for filtering
MIN_SIGNAL_DURATION = 0.05
signal_start_time = time.monotonic()

#___________________Joystiks Function______________________

DEFAULT_UP = 29536
DEFAULT_DOWN = 35000

ACTIVE_UP = 20536
ACTIVE_DOWN = 45000

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

#_____________________Giro to mouse________________________

# Initialize the shared I2C bus
i2c = busio.I2C(scl=board.D9, sda=board.D8)

# Initialize two ADXL345 sensors with different addresses
accelerometer_left = adafruit_adxl34x.ADXL345(i2c)
accelerometer_right = adafruit_adxl34x.ADXL345(i2c, address=0x53)     
    
SENSITIVITY = 30.0  # Adjust this value for faster or slower mouse movement



#___________________Working State______________________
while True:
    
    if not button_pressed:
        set_color(*DEFAULT_COLOR)  # Always set to the default color    

#___________________Keypad Matrix Function______________________
    scankeys()


#_____________________Giro to mouse________________________
    if mouse_movement_active == True:
        # Capture the baseline state when mouse_movement_active first becomes True
        # Read acceleration from both sensors
        left_x, left_y, left_z = accelerometer_left.acceleration
        right_x, right_y, right_z = accelerometer_right.acceleration
        
            # Round the values from the left sensor to two decimal places
        left_x = round(left_x, 2)
        left_y = round(left_y, 2)
        left_z = round(left_z, 2)

        # Round the values from the right sensor to two decimal places
        right_x = round(right_x, 2)
        right_y = round(right_y, 2)
        right_z = round(right_z, 2)

        # Calculate average X and Y movements from both sensors
        delta_x = ((left_x + right_x) / 2) * SENSITIVITY
        delta_y = ((left_z + right_z) / 2) * SENSITIVITY
    

        # Convert to integers for mouse movement
        mouse_x = int(-delta_x)
        mouse_y = int(-delta_y)

        # Move the mouse
        mouse.move(x=mouse_x, y=mouse_y)

    
#___________________Rotary Encoder Function______________________
    # Read the current state of the CLK pin
    current_clk_value = clk.value

    # Check if the encoder is turned and debounce
    if current_clk_value != previous_clk_value and (time.monotonic() - last_clk_time) > DEBOUNCE_DELAY:
        if current_clk_value == 0:  # Clockwise turn
            if dt.value == 0:  # If DT is low, it's a clockwise turn
                counter += 1
                if time.monotonic() - signal_start_time > MIN_SIGNAL_DURATION:
                    mouse.move(wheel=5)
                    signal_start_time = time.monotonic()  # Reset the signal timer
            else:  # If DT is high, it's a counterclockwise turn
                counter -= 1
                if time.monotonic() - signal_start_time > MIN_SIGNAL_DURATION:
                    mouse.move(wheel=-5)
                    signal_start_time = time.monotonic()  # Reset the signal timer

        # Update previous CLK value and last time
        previous_clk_value = current_clk_value
        last_clk_time = time.monotonic()

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
        keyboard.release(l_right_action)
    
    if l_y_value >= ACTIVE_DOWN:
        l_joystick_key_pressed.add(l_left_action)  # Add S key for "down"
    elif l_y_value <= DEFAULT_DOWN:
        keyboard.release(l_left_action)

# Detect X-axis movement (A and D keys)
    if l_x_value <= ACTIVE_UP:
        l_joystick_key_pressed.add(l_up_action)  # Add A key for "left"
    elif l_x_value >= DEFAULT_UP:
        keyboard.release(l_up_action)
    
    if l_x_value >= ACTIVE_DOWN:
        l_joystick_key_pressed.add(l_down_action)  # Add D key for "right"
    elif l_x_value <= DEFAULT_DOWN:
        keyboard.release(l_down_action)

# Press the keys currently in the `pressed_keys` set
    for key in l_joystick_key_pressed:
        keyboard.press(key)

#_____________________Right joystick________________________    


    r_x_value = read_axis(right_x_axis)
    r_y_value = read_axis(right_y_axis)

# Reset key states
    r_joystick_key_pressed = set()

# Detect Y-axis movement (W and S keys)
    if r_y_value <= ACTIVE_UP:
        r_joystick_key_pressed.add(r_right_action)  # Add W key for "up"  
    elif r_y_value >= DEFAULT_UP:
        keyboard.release(r_right_action)
    
    if r_y_value >= ACTIVE_DOWN:
        r_joystick_key_pressed.add(r_left_action)  # Add S key for "down"
    elif r_y_value <= DEFAULT_DOWN:
        keyboard.release(r_left_action)

# Detect X-axis movement (A and D keys)
    if r_x_value <= ACTIVE_UP:
        r_joystick_key_pressed.add(r_down_action)  # Add A key for "left"
    elif r_x_value >= DEFAULT_UP:
        keyboard.release(r_down_action)
    
    if r_x_value >= ACTIVE_DOWN:
        r_joystick_key_pressed.add(r_up_action)  # Add D key for "right"
    elif r_x_value <= DEFAULT_DOWN:
        keyboard.release(r_up_action)

# Press the keys currently in the `pressed_keys` set
    for key in r_joystick_key_pressed:
        keyboard.press(key)
    



 

