from nfc import NFCReader
import RPi.GPIO as GPIO
from time import sleep

from pinout import *

GPIO.setmode(GPIO.BOARD)

# TODO PWM doesn't seem to work

class Button:
    BOUNCETIME = 1000  # In milliseconds

    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def register_callback(self, onPressedCallback):
        def wrapped_callback(channel):
            print("Calling callback", channel)
            onPressedCallback()

        GPIO.add_event_detect(self.pin, GPIO.FALLING, callback=wrapped_callback, bouncetime=Button.BOUNCETIME)

class Led:
    PWM_FREQUENCY = 50  # 50 Hz

    def __init__(self, red_pin, green_pin, blue_pin):
        self.red_pin = red_pin
        self.green_pin = green_pin
        self.blue_pin = blue_pin

        GPIO.setup(self.pins, GPIO.OUT)

        self.pwm_for_channel = {}
        for pin in self.pins:
            self.pwm_for_channel[pin] = GPIO.PWM(pin, Led.PWM_FREQUENCY)

    @property
    def pins(self):
        return (self.red_pin, self.green_pin, self.blue_pin)

    def turn_on(self, red, green, blue):
        # Either simple output if max value, or PWM if not
        self._set_output(self.red_pin, red)
        self._set_output(self.green_pin, green)
        self._set_output(self.blue_pin, blue)

    def _set_output(self, channel, value):
        is_max = value == 255
        is_min = value == 0
        pwm = self.pwm_for_channel[channel]
        pwm.stop()

        if is_min:
            GPIO.output(channel, GPIO.LOW)
        elif is_max:
            GPIO.output(channel, GPIO.HIGH)
        else:
            # PWM
            pwm.start(value / 256)

    def turn_off(self):
        for pin in self.pins:
            self.pwm_for_channel[pin].stop()
            self._set_output(pin, 0)

class Hardware:
    previous_button = Button(PREV_BUTTON_PIN)
    next_button = Button(NEXT_BUTTON_PIN)
    pause_button = Button(PAUSE_BUTTON_PIN)

    led = Led(RED_CHANNEL, GREEN_CHANNEL, BLUE_CHANNEL)

    nfc_reader = NFCReader()

    def setup(self):
        pass

    def cleanup(self):
        GPIO.cleanup()

def get_uri(tag):
    pass


if __name__ == "__main__":
    button = Button(PREV_BUTTON_PIN)
    button.register_callback(lambda : print("Previous!"))

    try:
        led = Led(RED_CHANNEL, GREEN_CHANNEL, BLUE_CHANNEL)
        led.turn_on(0, 0, 255)
        sleep(1)
        led.turn_on(255, 0, 0)
        sleep(1)
        led.turn_on(0, 255, 0)
        sleep(1)
        led.turn_off()
    finally:
        GPIO.cleanup()
