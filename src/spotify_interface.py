import subprocess
from time import sleep
from utils import log

class SpotifyInterface:
    @log
    def setup(self):
        self._spotify("devices --switch-to RaspberryPi")
    
    def _spotify(self, command):
        arg = ["spotify"] + command.split(" ")
        subprocess.run(arg)
    
    @log
    def play(self, uri):
        self._spotify(f"play --uri {uri}")

    @log
    def pause(self):
        self._spotify("pause")

    @log
    def resume(self):
        self._spotify("play")

    @log
    def toggle(self):
        self._spotify("toggle")

    @log
    def next(self):
        self._spotify("next")

    @log
    def previous(self):
        self._spotify("previous")


if __name__ == "__main__":
    s = SpotifyInterface()
    s.setup()
    print("Starting test")

    s.play("spotify:album:5JY3b9cELQsoG7D5TJMOgw")
    sleep(1)
    s.toggle()
    sleep(1)
    s.toggle()
    s.next()