from hardware import Hardware, get_uri
from spotify_interface import SpotifyInterface

spotify = SpotifyInterface()
spotify.setup()

hardware = Hardware()
hardware.setup()


# Connect hardware with spotify
hardware.next_button.register_callback(spotify.next)
hardware.previous_button.register_callback(spotify.previous)
hardware.pause_button.register_callback(spotify.pause_or_resume)

# Tag reading loop
while True:
    tag = hardware.nfc_reader.read_tag()
    uri = get_uri(tag)
    spotify.play(uri)
    hardware.nfc_reader.wait_for_tag_removed()