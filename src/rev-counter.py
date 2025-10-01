from gpiozero import LED, Button, LEDBoard
from RPLCD.i2c import CharLCD
from time import sleep
import threading
import os

# ==============================
# Terminal styling & formatting
# ==============================
CURSOR_UP = '\033[1A'
CLEAR = '\x1b[2K'
CLEAR_LINE = CURSOR_UP + CLEAR

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

# ==============================
# Global variables
# ==============================
gear = 0        # Current gear
rpm = 0         # Current RPM
car_moving = 0  # Simple flag to track motion

lock = threading.Lock()  # Synchronization lock

# ==============================
# Hardware setup
# ==============================
leds = LEDBoard(14, 15, 18, 23, 24)   # 5 LEDs for shift light
lcd = CharLCD('PCF8574', 0x27, cols=16, rows=2)  # 16x2 LCD

ignition = Button(27, pull_up=False)  # Engine ON/OFF button
throttle = Button(5, pull_up=False)   # Blue button = Throttle
downshift = Button(6, pull_up=False)  # Yellow button = Downshift
upshift = Button(26, pull_up=False)   # Green button = Upshift

# ==============================
# Functions for car simulation
# ==============================

def acceleration():
    """Handle throttle input and update RPM accordingly."""
    global rpm, gear, car_moving
    while True:
        # If throttle is pressed, RPM rises depending on gear
        while throttle.is_pressed:
            sleep(0.048)
            with lock:
                if gear == 0:  # Neutral rev
                    rpm = min(rpm + 627, 9000)
                elif gear == 1:
                    car_moving = 1
                    rpm = min(rpm + 150, 9000)
                elif gear == 2:
                    car_moving = 1
                    rpm = min(rpm + 84, 9000)
                elif gear == 3:
                    car_moving = 1
                    rpm = min(rpm + 43, 9000)
                elif gear == 4:
                    car_moving = 1
                    rpm = min(rpm + 23, 9000)
                elif gear == 5:
                    car_moving = 1
                    rpm = min(rpm + 12, 9000)
                elif gear == 6:
                    car_moving = 1
                    if rpm > 8500:
                        rpm = min(rpm + 2, 9000)
                    else:
                        rpm = min(rpm + 5, 9000)

        # If throttle is released, RPM drops (engine braking or idle)
        while not throttle.is_pressed:
            sleep(0.048)
            with lock:
                if gear != 0 and rpm > 1200:
                    rpm = max(rpm - 50, 1200)
                elif gear == 0 and rpm > 1200:
                    rpm = max(rpm - 627, 1200)
                elif rpm == 1200:
                    car_moving = 0


def shift_up():
    """Increase gear and adjust RPM drop."""
    global rpm, gear
    while True:
        sleep(0.02)
        if upshift.is_pressed and gear < 6:
            with lock:
                gear = min(gear + 1, 6)
                if car_moving == 1:  # Only drop RPM if moving
                    drop_map = {2: 3200, 3: 2500, 4: 2000, 5: 1500, 6: 1200}
                    rpm = max(rpm - drop_map.get(gear, 0), 1200)
            sleep(0.2)  # Debounce button


def shift_down():
    """Decrease gear and adjust RPM rise."""
    global rpm, gear, car_moving
    while True:
        sleep(0.02)
        if downshift.is_pressed and gear > 0:
            with lock:
                gear = max(gear - 1, 0)
                if car_moving == 1:  # RPM rises only if moving
                    rpm = min(rpm + 1100, 9000)
            sleep(0.2)  # Debounce button


def display(): 
   global gear, rpm 
   lcd.clear() 
   lcd.write_string("Gear:       RPM:") 
   while True: 
      with lock: 
         lcd.cursor_pos = (1, 0) 
         lcd.write_string(f"{gear:<1}           {rpm:<4}") 
      sleep(0.15)

def flash_leds():
    """Control shift light LEDs based on RPM range."""
    global rpm
    while True:
        sleep(0.02)
        if rpm < 6500:
            leds.off()
        elif rpm < 7000:
            leds.on(0); leds.off(1, 2, 3, 4)
        elif rpm < 7500:
            leds.on(0, 1); leds.off(2, 3, 4)
        elif rpm < 8000:
            leds.on(0, 1, 2); leds.off(3, 4)
        elif rpm < 8500:
            leds.on(0, 1, 2, 3); leds.off(4)
        elif rpm < 8700:
            leds.on()
        else:
            # Flashing redline warning
            leds.off()
            sleep(0.1)
            leds.on()
            sleep(0.1)

# ==============================
# Main program flow
# ==============================

os.system("clear")

# Boot animation on LCD
lcd.cursor_pos = (0, 0)
lcd.write_string(" RPM simulator !")
lcd.cursor_pos = (1, 0)
lcd.write_string("________________")
sleep(5)
lcd.clear()
sleep(2)

lcd.cursor_pos = (0, 0)
lcd.write_string("  Engine: OFF  ")

print("To turn on the engine press the " + color.BOLD + "BLACK" + color.END + " button\n")

# Wait for ignition
while True:
    if ignition.is_pressed:
        rpm = 1200
        lcd.clear()
        print(CLEAR_LINE)
        sleep(3)
        break

# Startup sequence
leds.on(); sleep(0.2); leds.off()
lcd.cursor_pos = (0, 0)
lcd.write_string("   Engine ON    ")
sleep(1)

print("\nLoading")
for _ in range(3):
    sleep(1)
    print(" . ")
sleep(1)

os.system("clear")
sleep(0.5)

# Show button legend
print("Button legend:\n")
print(color.BLUE + "   BLUE" + color.END + ": Throttle")
print(color.YELLOW + "   YELLOW" + color.END + ": Shift down")
print(color.GREEN + "   GREEN" + color.END + ": Shift up")

# Start threads
threads = [
    threading.Thread(target=acceleration, daemon=True),
    threading.Thread(target=shift_up, daemon=True),
    threading.Thread(target=shift_down, daemon=True),
    threading.Thread(target=display, daemon=True),
    threading.Thread(target=flash_leds, daemon=True),
]

for t in threads:
    t.start()

# Keep main thread alive forever
while True:
    sleep(1)
