# Matrix Keypad
# NerdCave - https://www.youtube.com/channel/UCxxs1zIA4cDEBZAHIJ80NVg - Subscribe if you found this helpful.
# Github - https://github.com/Guitarman9119

from machine import Pin
import utime

# Create a map between keypad buttons and characters
matrix_keys = [['3', '2', '3', '4'],
               ['2', 'W', '5', 'R'],
               ['4', 'S', 'D', 'F'],
               ['1', 'X', 'C', 'V'],
               ['C', '6', '7', '8']]

# PINs according to schematic - Change the pins to match with your connections
keypad_rows = [0, 1, 2, 3, 4]
keypad_columns = [19, 20, 21, 22]

# Create two empty lists to set up pins ( Rows output and columns input )
col_pins = []
row_pins = []

# Loop to assign GPIO pins and setup input and outputs
for x in range(len(keypad_rows)):
    row_pins.append(Pin(keypad_rows[x], Pin.OUT))
    row_pins[x].value(1)
for x in range(len(keypad_columns)):
    col_pins.append(Pin(keypad_columns[x], Pin.IN, Pin.PULL_DOWN))
    col_pins[x].value(0)
    
##############################Scan keys ####################
    
print("Please enter a key from the keypad")
    
def scankeys():  
    for row in range(len(keypad_rows)):
        for col in range(len(keypad_columns)):
            row_pins[row].high()
            key = None
            
            if col_pins[col].value() == 1:
                print("You have pressed:", matrix_keys[row][col])
                key_press = matrix_keys[row][col]
                utime.sleep(0.3)
                    
        row_pins[row].low()

while True:
    scankeys()