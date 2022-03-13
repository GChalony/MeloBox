from hardware import Hardware, get_uri
from spotify_interface import SpotifyInterface

spotify = SpotifyInterface()
spotify.setup()

#spotify.play("spotify:playlist:37i9dQZF1DWWF3yivn1m3D")

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
        hardware.nfc_reader.wait_for_tag()
        print("Tag!")
        hardware.led.turn_on(0, 0, 255)
        uri = hardware.nfc_reader.read_tag()
        if uri is not None:
            spotify.play(uri)
        hardware.nfc_reader.wait_for_tag_removed()
        hardware.led.turn_on(0, 255, 0)
finally:
    hardware.cleanup()