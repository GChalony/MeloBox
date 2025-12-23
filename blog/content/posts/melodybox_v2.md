---
title: "The MelodyBox - v2"
date: 2025-12-20T21:29:14+02:00
---

![MEL](/MeloBox/front_v2.jpg)

This is the next iteration of the [MelodyBox]({{< ref "melodybox" >}}), a little box that plays music using floppy disks or pop figurines.

## Final result


{{< video src="/MeloBox/demo_v2.mp4">}}

{{< toc >}}


## Motivation: why a new one ?

I've been using the MelodyBox on and off for the last few years, but I kept on having some issues that I couldn't quite solve. It kept going for a while until some day, I decided to drop all the code and start from scratch. I later decide to remake the box, and that's how I arrived to this new version. Here is a little list of the issues that I had :
 - Spotify made regular changes, and `spotifyd` took too long to adapt. Fixes were available upstream though (in [`librespot`](https://github.com/librespot-org/librespot))
 - I wasn't super happy with how it looked
 - Quite buggy overall

## Software

I decide to try writing the code in Rust instead of Python, mostly as a training exercice. I encountered a lot of difficulties along the way, but I also learnt a lot. Here are a few important parts.

Rust has a "standard" called the `embedded-hal` traits, which describe some hardware capabilities : what is I2C, what is a GPIO etc... 

Here is a simplified version of the `I2c` trait:
```rust
pub trait I2c<A: AddressMode = SevenBitAddress>: ErrorType {
    /// Reads enough bytes from slave with `address` to fill `read`.
    fn read(&mut self, address: A, read: &mut [u8]) -> Result<(), Self::Error> {
        self.transaction(address, &mut [Operation::Read(read)])
    }

    /// Writes bytes to slave with address `address`.
    fn write(&mut self, address: A, write: &[u8]) -> Result<(), Self::Error> {
        self.transaction(address, &mut [Operation::Write(write)])
    }
```

So an `I2c` is anything that can read or write some bytes to a given adress. This trait can then be implemented differently on different hardware. For example, the [linux-embedded-hal](https://github.com/rust-embedded/linux-embedded-hal/) use the `/dev/i2c` vitual file provided by the OS, but [esp-idf-hal](https://github.com/esp-rs/esp-idf-hal) provides a completely different implementation for ESP32.

The brilliant part about this design, is that library authors can implement drivers for different hardware using these trait, without knowing the actual hardware it's running on. For example, the [`pn532`](https://github.com/WMT-GmbH/pn532/) crate can communicate with the PN532 (the NFC reader I'm using).

```rust
let i2c: I2c = I2c::new()?; // Create an I2c driver using Linux's /dev/i2c
let mut pn532: Pn532<_, _, 32> = Pn532::new(i2c, timer);

// Wait for a TAG
pn532.process(&Request::INLIST_ONE_ISO_A_TARGET, 16, timeout);

// Read a TAG's content
pn532.process(&Request::ntag_read(page), 20, timeout);
```

I have chosen [rppal](https://github.com/golemparts/rppal) which is specific to Raspberry Pis, but I encountered two issues :
 - there was an implementation bug, because `rppal` didn't implement the transaction part of I2C properly ([#171](https://github.com/golemparts/rppal/issues/171))
 - the Raspberry Pi 3B has a harware limitation with I2c, because it doesn't support clock stretching ([#27](https://github.com/WMT-GmbH/pn532/issues/27))

![I2C clock stretching](/MeloBox/i2c_clock_stretching.png)

 The solution wasn't too hard : I fixed the `Transaction` implementation, and used I2c with the interrupt pin, which means clock stretching is no longer an issue.

**Handling errors**

I still had two issues : the `Spotify` client disconnects after a while if not playing, and the `PN532` communication can sometimes be corrupted. These can probably be fixed, but I chose a different solution: pressing the "power" button restarts the program. That resets the Spotify client and PN532, and most of the time is enough to get it to work.
It's a naive workaround, but it my experience it's really useful, because I don't have to troubleshoot everytime it doesn't work.

{{< video src="/MeloBox/restart_animation.mp4" width="50%" >}}


## Hardware

I wanted to build something that would go well with my sound amplifier, so I figured I would make a new box in metal. I used 1.5mm thick inox, and a MIG to weld it all together. I made a homemade bender, to get nice rounder corners on the side. 
For the top, I drilled a big hole, so that the RF wave would not be blocked by the metal.

I did burn on raspberry pi because of a shortcircuit, so I learnt to put lots of tape inside to prevent any mistakes.

The last touch was to buy some better-looking buttons, for a more professional look. I used a button with an embedded led, to replace the previous setup.

|Lid open|The inside|
|-|-|
|![Lid open](/MeloBox/lid_open.jpg) |![Inside the box](/MeloBox/boombox_inside.jpg)|

## Conclusion

I'm really happy with this new version, it looks way better and works more reliably. It's always fun to have new people draw there floppy disks and try them out.
I have some thing that I'd like to work on though, which I'm listing it here so I can remember:
 - add a latch in the slot for floppy disk, so that you can push on it to eject it
 - turn off or deep sleep when not used
 - remove static sound hissing