#Blinking program

# incorporate/include modules
import machine #module with all the microcontroller stuff
import time #module with time methods
#Make the LED object
#Green LED is GPIO Pin 0
LED = machine.Pin(0,machine.Pin.OUT)
# Infinite loop
while True:
  LED.value(1) #turn on LED
  time.sleep(0.25) #0.25 second delay
  LED.value(0) #turn off LED
  time.sleep(0.25) #delay again