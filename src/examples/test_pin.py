from time import sleep
from RPi import GPIO

PIN = 5

GPIO.setmode(GPIO.BOARD)

GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        print("Value", GPIO.input(PIN))
        sleep(0.1)
finally:
    GPIO.cleanup()
