import subprocess
from time import sleep

class SpotifyInterface:
    def setup(self):
        pass
    
    def _spotify(self, command):
        arg = ["spotify"] + command.split(" ")
        subprocess.run(arg)
    
    def play(self, uri):
        self._spotify(f"play --uri {uri}")

    def pause(self):
        self._spotify("pause")

    def resume(self):
        self._spotify("play")

    def toggle(self):
        self._spotify("toggle")

    def next(self):
        self._spotify("next")

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