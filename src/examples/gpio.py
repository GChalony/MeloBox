import RPi.GPIO as GPIO
from time import sleep
from datetime import datetime

INTERRUPT_PIN = 32  # GPIO 16

GPIO.setmode(GPIO.BOARD)

GPIO.setup(INTERRUPT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

is_up = False
def on_interrupt(channel):
    global is_up
    is_up = not is_up
    print(is_up, GPIO.input(channel))
    print(datetime.now(), "Interrupted", channel, GPIO.input(channel))



try:
    GPIO.add_event_detect(INTERRUPT_PIN, GPIO.BOTH, callback=on_interrupt, bouncetime=100)
    # GPIO.add_event_detect(INTERRUPT_PIN, GPIO.FALLING, callback=on_interrupt)
    while True:
        sleep(1)
    
finally:
    GPIO.cleanup()