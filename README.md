# RaspberryPi RPM Simulator
A Raspberry Pi based RPM and gear simulator with shift LEDs and LCD display.

This is my first project — a Python program that simulates how throttle input and gear shifting affect engine RPM.  
The LCD displays the current gear and RPM, while LEDs act as a shift light. Buttons are used for throttle, ignition, and shifting.


## Features
- LCD shows current gear and RPM
- LEDs act as a progressive shift light
- Buttons simulate throttle, ignition, upshift, and downshift
- Real-time RPM simulation with smooth acceleration and deceleration


## Hardware
- Raspberry Pi 5
- 5 × LEDs + 5 330Ω resistors
- 4 × push buttons
- I²C LCD display with PCF8574 interface
- Breadboard + jumper wires


## Usage
- Press the **BLACK button** to turn on ignition
- Use the **BLUE button** for throttle
- Use the **GREEN button** to upshift
- Use the **YELLOW button** to downshift
- Watch the LCD for gear and RPM display
- LEDs light up progressively as RPM increases


## Installation
```bash
pip install -r requirements.txt
python3 rev-counter.py
```

## Circuit Diagram
![circuit](rev-counter_circuit1.png)


## Physical Build
![setup](setup.jpg)
