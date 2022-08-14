import base64
import json
import requests
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


class SpotifyWebAPI:
    BASE_URL = "https://api.spotify.com/v1"
    CLIENT_ID = "72100a4c5fb54d419ab71c5469cedbad"
    CLIENT_SECRET = "4f6f337860c241bf9c502280927fa226"

    PLAY_URL = BASE_URL + "/me/player/play"
    PAUSE_URL = BASE_URL + "/me/player/pause"
    PAUSE_URL = BASE_URL + "/me/player/next"
    _PATH_TO_SPOTIFY_CLI_CONFIG = "~/.config/spotify-cli/credentials.json"
    
    @property
    def auth_headers(self):
        return {"Authorization": "Bearer " + self.token, "Content-Type": "application/json"}

    def setup(self):
        # Get refresh token
        self.refresh_token = self.read_refresh_token()
        self.access_token = self.get_access_token(self.access_token)
        # Get device ID
        self.device_id = "f77ec2bda9ef8416d06f174358c03aaccbbd77e9"

    def read_refresh_token(self) -> str:
        with open(self._PATH_TO_SPOTIFY_CLI_CONFIG, "r") as config_file:
            credentials = json.load(config_file)
        return credentials["refresh_token"]
    
    @log
    def get_access_token(self, refresh_token: str) -> str:
        resp = requests.post("https://accounts.spotify.com/api/token", 
                      headers={"Authorization": "Basic " + self.b64(f"{self.CLIENT_ID}:{self.CLIENT_SECRET}")}, 
                      data={"grant_type": "refresh_token", "refresh_token": refresh_token})
        if resp.status_code != 200:
            raise RuntimeError("Couldn't refresh token: ", str(resp.content))
        content = json.loads(resp.content)
        return content["access_token"]

    @log
    def play(self, uri):
        requests.put(self.PLAY_URL + "?device_id=" + self.device_id, 
                    headers=self.auth_headers, 
                    json={"uris": [uri]})
    
    @log
    def toggle(self):
        requests.put(self.PAUSE_URL + "?device_id=" + self.device_id, 
                    headers=self.auth_headers)

    @log
    def next(self):
        requests.put(self.NEXT_URL + "?device_id=" + self.device_id, 
                    headers=self.auth_headers)

    def b64(self, string) -> str:
        return base64.b64encode(string.encode("utf-8")).decode("utf-8")


if __name__ == "__main__":
    s = SpotifyWebAPI()
    s.setup()
    print("Starting test")

    s.play("spotify:album:5JY3b9cELQsoG7D5TJMOgw")
    sleep(1)
    s.toggle()
    sleep(1)
    s.toggle()
    s.next()