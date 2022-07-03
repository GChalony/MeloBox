---
title: "The MelodyBox"
date: 2022-05-23T22:58:14+02:00
---


The MelodyBox is meant to give a physical support to music, as used to exist with vinyls and CDs. This requires two things :
 - a physical object that can identifying music
 - a reader which can read the music to play from the object and play it 

The object is an NFC tag, and the reader is an NFC reader coupled with a rasperryPi.

What is convenient about this is that the NFC tag can be embeded in almost any kind of object, as long as it doesn't intefere with the radiowaves used to read it. I have used floppy disks, a RubiksCube and Pop! figurines as such vectors.

The music is played through the spotify API, which has several advantages: any music on Spotify can be played (without having to download it locally first), we can create custom playlists to play and the playback can be controled from other Spotify devices, for example to change the volume or pause.

## Final result



## How it works

Alright, we know what we want to do, let's build it.

The first thing we need is to be able to play music.

pulseaudio, alsa
speakers, ampli, carte son

spotify
spotifyd
Spotify Web API
Interface : spotify-cli, MPRIS

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
Owning the NFC code
Interrupt


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

