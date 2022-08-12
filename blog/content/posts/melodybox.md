---
title: "The MelodyBox"
date: 2022-05-23T22:58:14+02:00
---


The MelodyBox is meant to give a physical support to music, as used to exist with vinyls and CDs. This requires two things :
 - a physical object that can identifying music
 - a reader which can read the music to play from the object and play it 

The object is an NFC tag, and the reader is an NFC reader coupled with a RasperryPi.

What is convenient about this is that the NFC tag can be embeded in almost any kind of object, as long as it doesn't intefere with the radiowaves used to read it. I have used floppy disks, a RubiksCube and Pop! figurines as such vectors.

The music is played through the spotify API, which has several advantages: any music on Spotify can be played (without having to download it locally first), we can create custom playlists to play and the playback can be controled from other Spotify devices, for example to change the volume or pause.

## Final result

Here's a demo of the result.

Freddy Mercury plays Queen music. The buttons can be used to pause/play, go to the next or the previous music. LEDs indicate whether a tag is detected or not, when a button is pressed etc...

## How it works

Alright, we know what we want to do, let's build it.

The first thing we need is to be able to play music.

We'll be using a RaspberryPi for this project. Indeed, we need a small enough board that it'll fit in a box, and it needs some pretty advanced features like connecting to spotify over the network or connecting to a NFC sensor. We could usea microcontroller, but it'd be so much work to add a network chip and all, while we get all that for free on a Pi.  
Also, as it's linux, we'll be able to use all the awesome tools that other people built for us!

> Disclaimer: we'll go through quite a few topics here, but I am by no means an expert. And though I'll try to give an overview of the technologies we'll manipulate, I'm more interested in _how to use them_ rather than _how they work_. I've left tons of ressources at the end if you want to go deeper.

### Playing sound

First of, we need speakers and to connect them to a Pi in a way that sound can be played. There are several ways to do that (passive / active speakers, different connectors, external sound card etc...) but we'll go for the simplest:
 - two passive speakers are connected to an amplifier, which provides power and sound directly (so they don't need to be connected to the sector)
 - the amplifier has a power input (sector) and can take several input types, both digital and analogic
 - the Pi's internal sound card convert digital sound to analogic, which is then forwarded to the ampli over a jack port

_scheme_

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

That's nice and all, but we want to be able to decide (programmatically) which song to play. That again needs to go through spotify's servers, and can be done with the [Spotify Web API](https://developer.spotify.com/documentation/web-api/). It's a bit annoying that we can't locally control the player, but it makes sense for spotify that it should be an intermediary.  
I won't present the API in details, the documentation is really good and should be enough. However, rather than using the API directly (which includes all kinds of credentials stuff), there's a nice cli program that can be useful, [spotify-cli](https://github.com/ledesmablt/spotify-cli).  
Once install, you can
```shell
# List available spotify devices
$ spotify devices -v
 * RaspeberryPi
 MyPhone
 ...
# Play a music
$ spotify play black summer
Playing: Black Summer
         Red Hot Chili Peppers - Black Summer
```

Rather than identifying songs with their name, which is annoying and sometimes ambiguous, songs, tracks and playlists are identified with Spotify URI. Here's [how to find the URI of a track](https://community.spotify.com/t5/FAQs/What-s-a-Spotify-URI/ta-p/919201).

We can then do
```shell
$ spotify play --uri spotify:album:5JY3b9cELQsoG7D5TJMOgw
```
Hooray!



MPRIS

We can now play a playlist, track or album with
```shell
spotify play --uri ...
```

Now comes the harder part : NFC.
We need :
 - to be able to detect when a tag is approached
 - to read the URI stored in the memory
 - detect when it is removed

Basic NFC concept
PN532 + NTAG210u


Putting it all together.

Box with buttons, leds.
    Turn on/off RaspberryPi.
    Buttons with interrupt
    Led for feedback
    Pinout

```python
def run():
    # Run the music server
    spotify.run()
    nfc.wait_for_tag()
```

Making a daemon
    systemd
    system dbus

Ideas for later optimisations
 - Owning the NFC code
 - Interrupt


### NFC

First, we need to communicate which music (album, playlist or track) using NFC. Near Field Communication is pretty complicated, especially because there are a lot of different standards, but the basic principal is quite simple :
 - a tag host some kind of memory (up to a few kB depending on the tag's type)
 - a reader creates a magnoeletric field near the tags
 - this induces current in the tag, which can use it to power its circuitry
 - both the reader and the tag can modulate the field to communicate, with a protocol described in the [IEE-14443].

 Tags can have pretty advanced features like authentication or memory locking, but the simplest one are :
 - identifying itself with a unique ID
 - read / write to a small memory

 We can use this memory to write a URI identifying which music we want to play, for example a Spotify URI : `spotify:album:5JY3b9cELQsoG7D5TJMOgw`. I use NFC Tool to flash the URI from a smartphone equiped with NFC. I used NTAG210u as they are cheap and small enough to be embeded in almost any object.

The reading is done with a PN532 chip, connected to a RaspberryPi over I2C. I initially chose I2C because it allows to plus multiple readers on the same pins, and even though I ended using only one reader, I stuck to this choice.

I struggled quite a lot to use the sensor, as I've found that there are not so many tools to use NFC in linux. The reference is `libnfc`, which is a librairie to use NFC, and also provides some tool to work with it. I've use `nfc-poll` quite a lot to wait for a tag to be detected.  
`libfreefare` is another library which build on top of it to provide more convenient APIs for MIFARE cards.  
I use `nfc-mfultralight` to read the content of the memory and parse it. I unfortunately didn't manage to use any other tool like `ntag-detect` or use the `pn532pi` python package.


![pinout](/MeloBox/rpi_pins.png)

![box](/MeloBox/box.svg)

