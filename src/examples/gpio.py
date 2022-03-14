import RPi.GPIO as GPIO
from time import sleep
from datetime import datetime

INTERRUPT_PIN = 7  # GPIO 4

GPIO.setmode(GPIO.BOARD)

GPIO.setup(INTERRUPT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def on_interrupt(channel):
    print(datetime.now(), "Interrupted", channel, GPIO.input(channel))



try:
    GPIO.add_event_detect(INTERRUPT_PIN, GPIO.RISING, callback=on_interrupt)
    while True:
        sleep(1)
    
finally:
    GPIO.cleanup()