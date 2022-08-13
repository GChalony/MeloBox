from nfc import NFCReader
import RPi.GPIO as GPIO
from time import sleep

from pinout import *

GPIO.setmode(GPIO.BOARD)

# TODO PWM doesn't seem to work

class Button:
    BOUNCETIME = 100  # In milliseconds

    def __init__(self, pin):
        self.pin = pin
        self.pressed_callbacks = []
        self.released_callbacks = []
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.pin, GPIO.BOTH, callback=self.interrupt_received, bouncetime=Button.BOUNCETIME)

    def register_pressed_callback(self, onPressedCallback):
        self.pressed_callbacks.append(onPressedCallback)

    def register_callback(self, onPressedCallback):
        self.register_pressed_callback(onPressedCallback)
    
    def register_released_callback(self, onReleasedCallback):
        self.released_callbacks.append(onReleasedCallback)

    def interrupt_received(self, channel):
        is_pressed = GPIO.input(self.pin) == 0
        print("Interrupt received", is_pressed)
        callback_list = self.pressed_callbacks if is_pressed else self.released_callbacks
        self.invoke_callbacks(callback_list)
    
    def invoke_callbacks(self, callback_list):
        for callback in callback_list:
            print("Invoking callback", callback.__name__)
            callback()

    

class Led:
    PWM_FREQUENCY = 50  # 50 Hz
    color = (0, 0, 0)

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
        self.color = (red, green, blue)

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
        self.color = (0, 0, 0)

class Hardware:
    previous_button = Button(PREV_BUTTON_PIN)
    next_button = Button(NEXT_BUTTON_PIN)
    pause_button = Button(PAUSE_BUTTON_PIN)

    led = Led(RED_CHANNEL, GREEN_CHANNEL, BLUE_CHANNEL)
    
    BUTTON_PRESSED_COLOR = (0, 255, 0)
    TAG_DETECTED_COLOR = (0, 0, 255)
    NO_TAG_COLOR = (255, 0, 0)

    nfc_reader = NFCReader()

    def setup(self):
        # Turn led green while button is pressed
        for button in [self.previous_button, self.pause_button, self.next_button]:
            button.register_pressed_callback(self.button_pressed)
            button.register_released_callback(self.button_released)

    def cleanup(self):
        GPIO.cleanup()

    def button_pressed(self):
        print("button pressed")
        self.led.turn_on(*self.BUTTON_PRESSED_COLOR)

    def button_released(self):
        led_color = self.TAG_DETECTED_COLOR if self.nfc_reader.tag_connected else self.NO_TAG_COLOR
        print("Restoring led", self.nfc_reader.tag_connected, led_color)
        self.led.turn_on(*led_color)


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
