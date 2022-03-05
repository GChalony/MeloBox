import RPi.GPIO as GPIO
from time import sleep

# Pins
PREV_BUTTON_PIN = 36  # GPIO 16
NEXT_BUTTON_PIN = 32  # GPIO 12
PAUSE_BUTTON_PIN = 37 # GPIO 26

pins = [PREV_BUTTON_PIN, NEXT_BUTTON_PIN, PAUSE_BUTTON_PIN]

GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
# Set pins to be an input pin and set initial value to be pulled low (off)
GPIO.setup(pins, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def poll():
    is_pushed = False
    while True: # Run forever
        input = not GPIO.input(PREV_BUTTON_PIN)
        if input and not is_pushed:
            print("Button was pushed!")
            is_pushed = True
        if not input and is_pushed:
            print("Released button")
            is_pushed = False

def interrupt():
    def callback(channel):
        print(f"From callback, {channel} was pressed")
    
    GPIO.add_event_detect(PREV_BUTTON_PIN, GPIO.FALLING, callback=callback, bouncetime=200)

    while True:
        sleep(1)
    # while True:
    #     channel = GPIO.wait_for_edge(PREV_BUTTON_PIN, GPIO.FALLING)
    #     print(channel, "pressed")

try:
    interrupt()
    
finally:
    GPIO.cleanup()