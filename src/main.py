#/usr/bin/python3

from hardware import Hardware, get_uri
from spotify_interface import SpotifyInterface
import signal


spotify = SpotifyInterface()
spotify.setup()

#spotify.play("spotify:playlist:37i9dQZF1DWWF3yivn1m3D")

hardware = Hardware()
hardware.setup()

# Catch SIGTERM signal to cleanup
def cleanup():
    print("See ya!")
    hardware.cleanup()
    spotify.pause()

signal.signal(signal.SIGTERM, cleanup)

# Connect hardware with spotify
hardware.next_button.register_callback(spotify.next)
hardware.previous_button.register_callback(spotify.previous)
hardware.pause_button.register_callback(spotify.toggle)

# Tag reading loop
try:
    while True:
        print("Waiting for tag")
        hardware.led.turn_on(255, 0, 0)
        hardware.nfc_reader.wait_for_tag()
        print("Tag!")
        hardware.led.turn_on(0, 255, 0)
        uri = hardware.nfc_reader.read_tag()
        hardware.led.turn_on(0, 0, 255)
        if uri is not None:
            spotify.play(uri)
        print("waiting for tag removed")
        hardware.nfc_reader.wait_for_tag_removed()
        spotify.pause()
finally:
    cleanup()