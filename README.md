# BoomBox

This project is meant to use a NFC sensor to play music through spotify.

The basic logic is :
 - Raspberry Pi connected to the internet and to speakers
 - `spotifyd` is running on it and playing music
 - NFC sensor (PN532) connected to it, will read NFC tags
 - Tags have a Spotify URI written to them, like `spotify:album:5JY3b9cELQsoG7D5TJMOgw`
 - When a tag is detected, the URI is read and passed to the Spotify Web API to play