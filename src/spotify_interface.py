import json
import subprocess
from time import sleep
from utils import log

class SpotifyInterface:
    @log
    def setup(self):
        # Switch to spotifyd device, retrying a few times in case of failure
        for i in range(5):
            self._spotify("devices --switch-to RaspberryPi")
            # Check if succeeded
            try:
                res = self._spotify("devices --verbose --raw", capture_output=True)
                response = res.stdout.decode("utf-8")
                print(response)
                devices = json.loads(response)
                for device in devices["devices"]:
                    if device["name"] == "RaspberryPi" and device["is_active"] == True:
                        print("Successfully changed device to RaspberryPi")
                        return
            except Exception as e:
                print("Error: ", e)
            print(f"Didn't swith device, will retry ({i} / 5)")
            sleep(1)


            
    
    def _spotify(self, command, **run_args):
        arg = ["spotify"] + command.split(" ")
        print("$", " ".join(arg))
        return subprocess.run(arg, **run_args)
    
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