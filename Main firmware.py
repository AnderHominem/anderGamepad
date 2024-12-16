from machine import Pin
import time
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse
import usb_hid

# Initialize HID devices
kbd = Keyboard(usb_hid.devices)
mouse = Mouse(usb_hid.devices)

# Pin definitions
keypad_rows = [0, 1, 2, 3, 4]  # Row GPIO pins
keypad_columns = [19, 20, 21, 22]  # Column GPIO pins

# Create row and column pin objects
row_pins = [Pin(pin, Pin.OUT) for pin in keypad_rows]
col_pins = [Pin(pin, Pin.IN, Pin.PULL_DOWN) for pin in keypad_columns]

# Define keymap for HID actions (customize as needed)
# Rows x Columns matrix
keymap = [
    [Keycode.A, Keycode.B, Keycode.C, Keycode.D],  # Row 0
    [Keycode.E, Keycode.F, Keycode.G, Keycode.H],  # Row 1
    [Keycode.I, Keycode.J, Keycode.K, Keycode.L],  # Row 2
    [Keycode.M, Keycode.N, Keycode.O, Keycode.P],  # Row 3
    ["MOUSE_LEFT", "MOUSE_RIGHT", "MOUSE_MIDDLE", None]  # Row 4
]

# State tracking for debouncing
key_states = [[False for _ in range(len(keypad_columns))] for _ in range(len(keypad_rows))]

def scan_matrix():
    """Scan the matrix for key presses."""
    pressed_keys = []
    for row_idx, row_pin in enumerate(row_pins):
        row_pin.value(1)  # Activate the row
        for col_idx, col_pin in enumerate(col_pins):
            if col_pin.value():  # Key is pressed
                pressed_keys.append((row_idx, col_idx))
        row_pin.value(0)  # Deactivate the row
    return pressed_keys

def handle_keypress(row, col, pressed):
    """Handle key press/release actions."""
    action = keymap[row][col]
    if action:
        if isinstance(action, str) and action.startswith("MOUSE_"):
            if action == "MOUSE_LEFT":
                if pressed:
                    mouse.press(Mouse.LEFT_BUTTON)
                else:
                    mouse.release(Mouse.LEFT_BUTTON)
            elif action == "MOUSE_RIGHT":
                if pressed:
                    mouse.press(Mouse.RIGHT_BUTTON)
                else:
                    mouse.release(Mouse.RIGHT_BUTTON)
            elif action == "MOUSE_MIDDLE":
                if pressed:
                    mouse.press(Mouse.MIDDLE_BUTTON)
                else:
                    mouse.release(Mouse.MIDDLE_BUTTON)
        elif isinstance(action, Keycode):
            if pressed:
                kbd.press(action)
            else:
                kbd.release(action)

def main():
    """Main loop to scan and handle key presses."""
    global key_states
    while True:
        pressed_keys = scan_matrix()
        new_states = [[False for _ in range(len(keypad_columns))] for _ in range(len(keypad_rows))]

        for row, col in pressed_keys:
            new_states[row][col] = True

        for row in range(len(keypad_rows)):
            for col in range(len(keypad_columns)):
                if new_states[row][col] != key_states[row][col]:
                    handle_keypress(row, col, new_states[row][col])

        key_states = new_states
        time.sleep(0.01)  # Debounce delay

if __name__ == "__main__":
    main()
