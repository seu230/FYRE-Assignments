# Team Members Names: Samuel, Micah, Brandon
# Purpose of the Code: The purpose of the code was to turn an arm connected to a Servo motor 180 degrees
# Date Code was Started: 9/16/2026
# Date of Last Update: 9/16/2026
# Explanation of AI Use: Used to generate the code which the program ran off of.

from machine import Pin, PWM
import time

# -------------------------
# Pin setup
# -------------------------

# Nano ESP32:
# A6 = GPIO13
# D5 = GPIO8

button = Pin(13, Pin.IN, Pin.PULL_UP)
servo = PWM(Pin(8), freq=50)

# -------------------------
# Servo position function
# -------------------------

def set_servo_angle(angle):
    # Typical servo pulse widths:
    # 0 degrees   = 500 us
    # 180 degrees = 2500 us

    pulse_us = 500 + (angle * 2000 // 180)

    # Convert microseconds to nanoseconds
    servo.duty_ns(pulse_us * 1000)


# Start servo at 0 degrees
set_servo_angle(0)

# False = 0 degrees
# True  = 180 degrees
servo_at_180 = False

# Remember previous button state
last_button = 1

# -------------------------
# Main loop
# -------------------------

while True:

    button_state = button.value()

    # Button is pressed when the pin reads LOW
    # Detect only the transition from HIGH -> LOW
    if button_state == 0 and last_button == 1:

        # Toggle the servo position
        if servo_at_180 == False:
            set_servo_angle(180)
            servo_at_180 = True
        else:
            set_servo_angle(0)
            servo_at_180 = False

        # Small delay to prevent button bounce
        time.sleep_ms(300)

    last_button = button_state

    time.sleep_ms(10)