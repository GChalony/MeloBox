---
title: "The MelodyBox"
date: 2022-05-23T22:58:14+02:00
---

![MEL](/MeloBox/front_photo.png)

The MelodyBox is meant to give a physical support to music, as used to exist with vinyls and CDs. This requires two things :
 - a physical object that can identifying music
 - a reader which can read the music to play from the object and play it 

The object is an NFC tag, and the reader is an NFC reader coupled with a RasperryPi.

What is convenient about this is that the NFC tag can be embeded in almost any kind of object, as long as it doesn't intefere with the radiowaves used to read it. I have used floppy disks, a RubiksCube and Pop! figurines as such vectors.

The music is played through the spotify API, which has several advantages: any music on Spotify can be played (without having to download it locally first), we can create custom playlists to play and the playback can be controled from other Spotify devices, for example to change the volume or pause.

## Final result

Here's a demo of the result.

![Video demo](/MeloBox/demo.gif)

Freddy Mercury plays Queen music. The buttons can be used to pause/play, go to the next or the previous music. LEDs indicate whether a tag is detected or not, when a button is pressed etc...

{{< toc >}}

## How it works

Alright, we know what we want to do, let's build it.

The first thing we need is to be able to play music.

We'll be using a RaspberryPi for this project. Indeed, we need a small enough board that it'll fit in a box, and it needs some pretty advanced features like connecting to spotify over the network or connecting to a NFC sensor. We could usea microcontroller, but it'd be so much work to add a network chip and all, while we get all that for free on a Pi.  
Also, as it's linux, we'll be able to use all the awesome tools that other people built for us!

_**Disclaimer**: we'll go through quite a few topics here, but I am by no means an expert. And though I'll try to give an overview of the technologies we'll manipulate, I'm more interested in _how to use them_ rather than _how they work_. I've left tons of ressources at the end if you want to go deeper._

### Playing sound

First of, we need speakers and to connect them to a Pi in a way that sound can be played. There are several ways to do that (passive / active speakers, different connectors, external sound card etc...) but we'll go for the simplest:
 - two passive speakers are connected to an amplifier, which provides power and sound directly (so they don't need to be connected to the sector)
 - the amplifier has a power input (sector) and can take several input types, both digital and analogic
 - the Pi's internal sound card convert digital sound to analogic, which is then forwarded to the ampli over a jack port

![speakers wiring](/MeloBox/schema_speakers.png)

 To test the setup, just run `speaker-test` and check that the speakers are playing a nice white noise (perfect to go to sleep).

### Sound architecture in linux

Playing sound on linux is not as straightforward as sending the digital data directly to the DAC (Digital-to-Analog-Converter, i.e. the sound card). All harware is usually handled by the kernel, so we need a way to ask the kernel to play sound.  
The prime interface is called ALSA, for [Advanced Linux Sound Architecture](https://en.wikipedia.org/wiki/Advanced_Linux_Sound_Architecture). Application can send data they want to play to ALSA, and it will take care of it, optionnaly mixing multiple inputs (if you're playing both Youtube and Spotify).  
Here are a few commands to poke around:

```shell
# List all outputs available
$ aplay -L
...
jack
    JACK Audio Connection Kit
# Play a WAV file
$ aplay some_music.wav
... plays
```


However, ALSA is now rarely directly used, as it was replaced by [PulseAudio](https://en.wikipedia.org/wiki/PulseAudio) as the interface to applications. PulseAudio runs as a background process (the server), and offers a much more powerful interface for applications to play sound : volume control per application, multiple outputs, a nice daemon to control its settings etc... PulseAudio builds on top of ALSA, but also registers as an ALSA device, which is why a PulseAudio entry is listed in `aplay -L` output.  


```shell
# List available outputs
$ pactl list sinks
Sink #0
	State: SUSPENDED
	Name: alsa_output.platform-bcm2835_audio.analog-stereo
	Description: Built-in Audio Analog Stereo
...
# Play a WAV file
$ pacat some_music.wav
# List applications currently playing sound
$ pactl list sink-inputs | grep application.name
application.name = "speech-dispatcher-dummy"
module-stream-restore.id = "sink-input-by-application-name:speech-dispatcher-dummy"
application.name = "pacat"
module-stream-restore.id = "sink-input-by-application-name:pacat"
```


Alright, we now know how to play music locally. However, our goal is to use spotify so that we can play almost any music, rather than only what I have on my computer.

### Playing with Spotify

Playing music through spotify requires two things : a client and a controller. The client is in charge of receiving the music data from spotify and playing it locally (through PulseAudio as we've just seen). The controller is in charge of - you guessed it - controlling the music to play.

The official spotify client is provided by Spotify, that's the full desktop app we're used to. However, that's not very convenient for an embedded system as the pi : it requires a whole desktop to be installed just to run an app.  
Which is why some amazing people have built [spotifyd](https://github.com/Spotifyd/spotifyd), which is a lightweight spotify client (it builds on [librespot](https://github.com/librespot-org/librespot) which is the actual client). Follow the instructions on their repo to install it locally. I chose to build it manually, I'll explain why later.  
Once installed, setup the configuration in the `~/.config/spotifyd/spotifyd.conf`. You can see mine on [my repo](https://github.com/GChalony/MeloBoxhttps://github.com/GChalony/MeloBox).

When all that is done, you should be able to run it with
```shell
$ spotifyd --no-daemon
Loading config from "/home/pi/.config/spotifyd/spotifyd.conf"
No proxy specified
Using software volume controller.
Connecting to AP "ap.spotify.com:443"
Authenticated as "...." !
Country: "FR"
Using Alsa sink with format: S16
```

If you have another device (for example a phone) connected on the same network, you should now see this as an available player in Spotify's app. Spotify uses [ZeroConf](https://flylib.com/books/en/2.94.1.16/1/) under the hood to broadcast itself to all others on the network, which is pretty convenient. If you select this device, you should be able to play any song directly on the Pi. Congratulations, you got yourself a network speaker!

That's nice and all, but we want to be able to decide (programmatically) which song to play. That again needs to go through spotify's servers, and can be done with the [Spotify Web API](https://developer.spotify.com/documentation/web-api/). 

I won't present the API in details, the documentation is really good and should be enough. Assuming we have an access token stored in `ACCESS_TOKEN` (we'll get back to it), we can:

```shell
# Get some info about current playback
$ curl https://api.spotify.com/v1/me/player \
  --header "Authorization: Bearer $ACCESS_TOKEN" \
  --header 'Content-Type: application/json'
{
  "device" : {
    "id" : "f77ec2bda9ef8416d06f174358c03aaccbbd77e9",
    "is_active" : true,
    "name" : "RaspberryPi",   <-- The spotifyd player
    "type" : "Speaker",
    "volume_percent" : 89
  },
  ...
  "is_playing" : true
}
# Pause playback
$ curl --request PUT https://api.spotify.com/v1/me/player/pause \
  --header "Authorization: Bearer $TOKEN" \
  --header 'Content-Type: application/json'
# Play an album
$ curl --request PUT https://api.spotify.com/v1/me/player/play \
  --header "Authorization: Bearer $TOKEN" \
  --header 'Content-Type: application/json' \
  --data '{"context_uri": "spotify:album:5JY3b9cELQsoG7D5TJMOgw"}'
```


> Rather than identifying songs with their name, which is annoying and sometimes ambiguous, songs, tracks and playlists are identified with Spotify URI. Here's [how to find the URI of a track](https://community.spotify.com/t5/FAQs/What-s-a-Spotify-URI/ta-p/919201).


To avoid writing the requests manually, there's a nice cli program that can be useful, [spotify-cli](https://github.com/ledesmablt/spotify-cli). This tool is really nice, especially because the developper made a nice little server to handle authentication. Without getting into too much details (read [Spotify's Authorization Code Flow](https://developer.spotify.com/documentation/general/guides/authorization/code-flow/)), I decided it'd be much simpler to use `spotify-cli`'s refresh token, which is stored in `~/.config/spotify-cli/credentials.json`, which means we can simply use it to get an access token when need and that's it.


To sum up, we're now able to play a desired music / album either through the API or with:
```shell
$ spotify play --uri spotify:album:5JY3b9cELQsoG7D5TJMOgw
```
Hooray!

However, we can still do better. I was frustrated that we had to use the API even to just pause the song or skip to the next one, and then I found [MPRIS](https://specifications.freedesktop.org/mpris-spec/latest/). MPRIS is a protocol that works over [DBUS](https://dbus.freedesktop.org/doc/dbus-specification.html) and allows processes to control media players. That's a lot of new words, so let's split it up.

D-BUS is a way for processes to communicate between each other. This can be useful for lots of different reasons, for example is a process wishes to expose commands to control it. You can view the traffic over dbus with 
```shell
$ dbus-monitor
```
You'll see there's all kind of communication between applications.

MPRIS (Media Player Remote Interfacing Specification) is a protocol that builds on top of DBUS, with which media playing applications (like your music player, Netflix or VLC) can allow other applications to control them.  
Thanksfully, `spotifyd` supports MPRIS (with the `use_mpris = true` set in the config file). That means we can do

```python
>>> bus = dbus.SystemBus()  # communicate with spotifyd over system bus
>>> player = bus.get_object("org.mpris.MediaPlayer2.spotifyd", "/org/mpris/MediaPlayer2")
>>> interface = dbus.Interface(self.player, dbus_interface='org.mpris.MediaPlayer2.Player')

# Play a URI
>>> interface.OpenUri("spotify:album:5JY3b9cELQsoG7D5TJMOgw")
# Toggle play / pause
>>> interface.PlayPause()
# Skip to next song
>>> interface.Next()
```

Nice ! As this communicates directly between our program and `spotifyd`, there's no latency due to communication with spotify.

We now know how to programmatically control the music being played with spotify. That's already pretty cool, but we're missing the most important: NFC!

### NFC

Near Field Communication is pretty complicated, especially because there are a lot of different standards, but the basic principal is quite simple :
 - a tag host some kind of memory (up to a few kB depending on the tag's type)
 - a reader creates a magnoeletric field near the tags
 - this induces current in the tag, which can use it to power its circuitry
 - both the reader and the tag can modulate the field to communicate, with a protocol described in the [IEE-14443].

 Tags can have pretty advanced features like authentication or memory locking, but the simplest one are :
 - identifying itself with a unique ID
 - read / write to a small memory

 We can use this memory to write a URI identifying which music we want to play, for example a Spotify URI : `spotify:album:5JY3b9cELQsoG7D5TJMOgw`. I use NFC Tool to flash the URI from a smartphone equiped with NFC. I used NTAG210u as they are cheap and small enough to be embeded in almost any object.

The reading is done with a PN532 chip, connected to a RaspberryPi over I2C. I initially chose I2C because it allows to use multiple readers on the same pins, and even though I ended using only one reader, I stuck to this choice.

![pn532](/MeloBox/pn532.jpg)

The base library to handle NFC in linux is [libnfc](https://github.com/nfc-tools/libnfc). [libfree](https://github.com/nfc-tools/libfreefare) builds on top of it to provide more convenient APIs and handle some custom features. Both come with a set of cli utilities to use nfc:
```shell
# Detect when a tag is moved close to the sensor
$ nfc-poll
...
$ nfc-mfultralight r card.dump  
```
The file written by `nfc-mfultralight` contains a dump of the memory stored in the tag, and can then be read:
```shell
$ hexdump card.dump -C
00000000  04 71 9b 66 0a 92 72 81  6b 48 00 00 e1 10 06 00  |.q.f..r.kH......|
00000010  03 2b d1 01 27 54 02 65  6e 73 70 6f 74 69 66 79  |.+..'T.enspotify|
00000020  3a 61 6c 62 75 6d 3a 32  72 43 53 36 58 77 78 33  |:album:2rCS6Xwx3|
00000030  32 56 32 37 70 76 67 46  7a 4c 7a 6c 54 fe 00 00  |2V27pvgFzLzlT...|
```
We can then easily parse it to get the spotify uri. There probably is a specification concerning the format of the file ([NFC Data Exchange Format - NDEF](https://learn.gototags.com/nfc/ndef) and [MAD](https://www.d-logic.com/knowledge_base/mifare-classic-and-mifare-plus-ic-memory-mapping-of-ndef-data/)) but I'm just basing it on the file I have at hand. 

And that's it! We now have all the tools to do what we want: play the music defined by the tag. In pseudo code, here's what i looks like:

```python
while wait_for_tag():
  spotify_uri = read_tag_uri()
  spotify.play(spotify_uri)
```

We now have a functioning prototype :) 

### Making a box

Now that we've done all that, we need to make a nice little box and some user interface to avoid having to start it from SSH every time.

As always, the devil is in the details, but I won't mention it all here - the article is already too long as it is.

I came up with this design.

{{< columns >}}
![box](/MeloBox/box-3d.png)
{{< column >}}
![box](/MeloBox/box-real.jpg)
{{< endcolumns >}}

The power button has an led indicator to show when the Pi is turned on. Three buttons control the playback (previous, play/pause and next). A slot accepts a floppy disk, with NFC tags. Otherwise, a figurine (or really any object) with a tag can be put above. A little RGB-LED on the side gives some feedback on what is happening (red when no tag, blue when one is detected, green when a button is pressed).

![box](/MeloBox/open_box.jpg)
_The mess inside_

I used `systemd` to autostart the program when the Pi is turned on. It's also really useful to gather the logs, or to automatically restart it when it fails.

## Final thoughts

 - overheating
 - NFC manual implementation
 - interrupt
 - power on / off
 - write in Rust


## Sources

[Adding a power button with LED indicator](https://embeddedcomputing.com/technology/open-source/development-kits/raspberry-pi-power-up-and-shutdown-with-a-physical-button)
