from hardware import Hardware, get_uri
from spotify_interface import SpotifyInterface

spotify = SpotifyInterface()
spotify.setup()

spotify.play("spotify:playlist:37i9dQZF1DWWF3yivn1m3D")

hardware = Hardware()
hardware.setup()


hardware.led.turn_on(0, 255, 0)

# Connect hardware with spotify
hardware.next_button.register_callback(spotify.next)
hardware.previous_button.register_callback(spotify.previous)
hardware.pause_button.register_callback(spotify.toggle)

# Tag reading loop
try:
    while True:
        tag = hardware.nfc_reader.read_tag()
        uri = get_uri(tag)
        #spotify.play(uri)
        hardware.nfc_reader.wait_for_tag_removed()
finally:
    hardware.cleanup()