from time import sleep
from RPi import GPIO

from pinout import POWER_LED

GPIO.setmode(GPIO.BOARD)

GPIO.setup(POWER_LED, GPIO.OUT)
GPIO.output(POWER_LED, GPIO.HIGH)

try:
    while True:
        sleep(1)
finally:
    GPIO.cleanup()
