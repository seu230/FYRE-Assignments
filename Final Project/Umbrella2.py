from machine import Pin, ADC, PWM
import time

# Group Members: Micah Oliveri-Schneider, Samuel Underwood, Brandon Nguyen
# When the humidity sensor reaches an ADC reading of 5 or greater, the umbrella arm goes up and the red LED starts blinking. When the contact switch is pressed, the umbrella goes down and the LED turns off.
# This prototype is meant to simulate an automatic umbrella that warns someone when it is raining and keeps them dry.
# Sept. 28 Update: The rate of LED flashing now relates to the intensity of rain falling. For every increase by 5 on the ADC, the flashing speed is multiplied by 1.5

# ============================================================
# PIN ASSIGNMENTS
# ============================================================

WATER_SENSOR_PIN = "A1"   # Custom two-wire water sensor
RED_LED_PIN = "D4"        # Red LED
SWITCH_PIN = "A7"         # Push-button / contact switch
SERVO_PIN = "A4"          # 9g micro servo

# ============================================================
# WATER SENSOR SETTINGS
# ============================================================

# The umbrella will go UP when the ADC reading is 5 or greater.
THRESHOLD = 5

# Print the ADC reading every 0.5 seconds
SENSOR_INTERVAL = 500  # milliseconds

# ============================================================
# SERVO SETTINGS
# ============================================================

# Umbrella DOWN position
START_ANGLE = 0

# Umbrella UP position
# This is exactly 90 degrees from the starting position.
UP_ANGLE = 90

# Servo pulse width limits for a typical 9g servo
MIN_PULSE_US = 500
MAX_PULSE_US = 2500

# ============================================================
# LED SETTINGS
# ============================================================

# Starting LED blink interval
BASE_BLINK_INTERVAL = 500  # milliseconds

# LED blinking speed increases by 1.5x for every
# increase of 5 ADC readings above the threshold.

# ============================================================
# SET UP HARDWARE
# ============================================================

# Water sensor ADC
water_sensor = ADC(Pin(WATER_SENSOR_PIN))

# Use 12-bit ADC readings: 0-4095
try:
    water_sensor.width(ADC.WIDTH_12BIT)
except AttributeError:
    pass

# Red LED
red_led = Pin(RED_LED_PIN, Pin.OUT)
red_led.off()

# Push button / contact switch
# Assumes the switch connects the pin to GND when pressed.
switch = Pin(SWITCH_PIN, Pin.IN, Pin.PULL_UP)

# Servo
servo = PWM(Pin(SERVO_PIN), freq=50)


# ============================================================
# SERVO FUNCTION
# ============================================================

def set_servo_angle(angle):
    """Move the servo to the requested angle."""

    if angle < 0:
        angle = 0

    if angle > 180:
        angle = 180

    pulse_us = MIN_PULSE_US + (
        (MAX_PULSE_US - MIN_PULSE_US) * angle / 180
    )

    # 50 Hz = 20,000 microseconds per period
    duty = int((pulse_us / 20000) * 65535)

    servo.duty_u16(duty)


# ============================================================
# UMBRELLA STATES
# ============================================================

DOWN = 0
UP = 1

state = DOWN

# Start with umbrella DOWN
set_servo_angle(START_ANGLE)
red_led.off()


# ============================================================
# TIMING VARIABLES
# ============================================================

last_sensor_time = time.ticks_ms()
last_led_time = time.ticks_ms()

# Store the most recent ADC value
adc_value = 0

# LED starts OFF
led_state = False

# Button debounce variables
last_raw_switch = switch.value()
stable_switch = last_raw_switch
last_switch_change = time.ticks_ms()

DEBOUNCE_TIME = 50  # milliseconds


# ============================================================
# STARTUP MESSAGE
# ============================================================

print("Umbrella prototype started.")
print("Umbrella is DOWN.")
print("Water sensor threshold:", THRESHOLD)


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    now = time.ticks_ms()

    # --------------------------------------------------------
    # WATER SENSOR
    # --------------------------------------------------------

    if time.ticks_diff(now, last_sensor_time) >= SENSOR_INTERVAL:

        last_sensor_time = now

        adc_value = water_sensor.read()

        # Print the raw ADC value for testing
        print("Water Sensor ADC:", adc_value)

        # If the umbrella is DOWN and the ADC reading is
        # 5 or greater, move the umbrella UP.
        if state == DOWN and adc_value >= THRESHOLD:

            print("ADC reading is 5 or greater.")
            print("Water detected! Umbrella moving UP.")

            # Move servo 90 degrees
            set_servo_angle(UP_ANGLE)

            # Change state to UP
            state = UP

            # Turn LED on immediately
            led_state = True
            red_led.on()

            # Reset LED blink timer
            last_led_time = now

    # --------------------------------------------------------
    # BLINK RED LED WHILE UMBRELLA IS UP
    # --------------------------------------------------------

    if state == UP:

        # Determine how many groups of 5 ADC readings are
        # above the threshold.
        #
        # Example:
        # ADC 5-9   = 1x speed
        # ADC 10-14 = 1.5x speed
        # ADC 15-19 = 2.25x speed
        # ADC 20-24 = 3.375x speed
        #
        # Increasing the speed means decreasing the time
        # between LED changes.

        if adc_value >= THRESHOLD:
            steps = (adc_value - THRESHOLD) // 5
        else:
            steps = 0

        blink_interval = int(
            BASE_BLINK_INTERVAL / (1.5 ** steps)
        )

        # Keep the LED from reaching an impractically fast
        # blink interval.
        if blink_interval < 10:
            blink_interval = 10

        # Blink using the calculated interval
        if time.ticks_diff(now, last_led_time) >= blink_interval:

            last_led_time = now

            led_state = not led_state

            if led_state:
                red_led.on()
            else:
                red_led.off()

    else:

        # LED must stay OFF while umbrella is DOWN
        led_state = False
        red_led.off()

    # --------------------------------------------------------
    # CONTACT SWITCH WITH DEBOUNCING
    # --------------------------------------------------------

    raw_switch = switch.value()

    # Detect a change in the button signal
    if raw_switch != last_raw_switch:

        last_raw_switch = raw_switch
        last_switch_change = now

    # Wait until the button signal is stable
    if time.ticks_diff(now, last_switch_change) >= DEBOUNCE_TIME:

        if raw_switch != stable_switch:

            stable_switch = raw_switch

            # LOW means the button is pressed
            if stable_switch == 0:

                # Only reset the umbrella if it is UP
                if state == UP:

                    print("Contact switch pressed.")
                    print("Umbrella moving DOWN.")

                    # Return servo to starting position
                    set_servo_angle(START_ANGLE)

                    # Change state to DOWN
                    state = DOWN

                    # Turn LED OFF
                    led_state = False
                    red_led.off()

                    # Reset blink timer
                    last_led_time = now

    # Small delay that does not interfere with the main logic
    time.sleep_ms(10)