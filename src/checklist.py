# Run a checklist to verify that every thing works correctly

from dataclasses import dataclass
from pinout import *
import RPi.GPIO as GPIO

@dataclass
class ChecklistItem:
    success: bool
    description: str

checklist = []

def test_output_pin(pin, text):
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)
    r = input(f"Do you see {text} ON ? [y/n] ")
    GPIO.output(pin, GPIO.LOW)
    return ChecklistItem(r == "y", text)

def test_button_low(pin, text):
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    print(f"Press button {text}")
    channel = GPIO.wait_for_edge(pin, GPIO.FALLING, timeout=20000)
    success = not channel is None
    if success:
        print("OK!")
    return ChecklistItem(success, text)


# Setup
GPIO.setmode(GPIO.BOARD)

# RGB LED
checklist.append(test_output_pin(RED_CHANNEL, "RED LED"))
checklist.append(test_output_pin(GREEN_CHANNEL, "GREEN LED"))
checklist.append(test_output_pin(BLUE_CHANNEL, "BLUE LED"))

# Button LED
checklist.append(test_output_pin(POWER_LED, "Power LED"))

# Power button
checklist.append(test_button_low(POWER_BUTTON, "Power button"))

# Player buttons
checklist.append(test_button_low(PREV_BUTTON_PIN, "Previous button"))
checklist.append(test_button_low(PAUSE_BUTTON_PIN, "Pause button"))
checklist.append(test_button_low(NEXT_BUTTON_PIN, "Next button"))

GPIO.cleanup()

print("================= RESULT =================")
for item in checklist:
    color = "\033[" + ("32" if item.success else "31") + "m"
    reset = "\033[0m"
    print(f"{color}{item.description}\t : \t{item.success}{reset}")
