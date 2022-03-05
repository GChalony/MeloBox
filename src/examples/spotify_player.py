import errno
import logging
from typing import Sequence, Union

from spotipy.client import Spotify
from spotipy.oauth2 import SpotifyOAuth

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class NoDeviceError(Exception): pass

class SpotifydClient:
    id = "783e33e821f592ca2f98b67853b02cf46030ced3"

class Player:
    def __init__(self) -> None:
        scope = "user-read-playback-state,user-modify-playback-state"
        # TODO hide all that
        self.client = Spotify(
            client_credentials_manager=SpotifyOAuth(
                "72100a4c5fb54d419ab71c5469cedbad",
                "4f6f337860c241bf9c502280927fa226",
                "http://localhost:8888/callback",
                scope=scope
            )
        )
    
    def start(self):
        devices = self.client.devices()["devices"]
        
        if len(devices) == 0:
            raise NoDeviceError
        
        logger.debug(f"Found devices: {devices}")
        # By default use first device
        device = devices[0]
        if not device["is_active"]:
            self.client.transfer_playback(device["id"])


    def play(self, uri: Union[str, Sequence[str]]):
        if isinstance(uri, str):
            if "playback" in uri:
                self.client.start_playback(context_uri=uri)
            elif "track" in uri:
                self.client.start_playback(uris=[uri])
        else:
            self.client.start_playback(uris=uri)
    
    def stop(self):
        self.client.pause_playback()

if __name__ == "__main__":
    import os
    from pathlib import Path
    
    fifo = Path(__file__).parent / "spotify_fifo"
    try:
        os.mkfifo(fifo)
    except OSError as oe: 
        if oe.errno != errno.EEXIST:
            raise
    
    p = Player()
    p.start()

    try:
        while True:
            print("Opening FIFO")
            with open(fifo, "r") as input:
                while True:
                    uri = input.read()
                    if len(uri) == 0:
                        break
                    print("Received", uri)
                    p.play(uri)
            print("Closing FIFO")
    
    finally:
        p.stop()
        