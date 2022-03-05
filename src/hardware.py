from src.nfc import NFCReader


class Button:
    def register_callback(onPressedCallback):
        pass

class Led:
    def turn_on(rgb):
        pass

    def turn_off():
        pass

class Hardware:
    previous_button = Button()
    next_button = Button()
    pause_button = Button()

    led = Led()

    nfc_reader = NFCReader()

    def setup(self):
        pass

def get_uri(tag):
    pass


