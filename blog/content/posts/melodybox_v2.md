---
title: "The MelodyBox - v2"
date: 2025-12-20T21:29:14+02:00
---

This is the next iteration of the Melodybox, a little box that plays music using floppy disks or pop figurines.

## Final result


## Motivation: why a new one ?

I've been using the MelodyBox on and off for the last few years, but I kept on having some issues that I couldn't quite solve. It kept going for a while until some day, I decided to drop all the code and start from scratch. I later decide to remake the box, and that's how I arrived to this new version.

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

I have chosen [rppal](https://github.com/golemparts/rppal) which is specific to Raspberry Pis, but I encountered two issues :
 - there was an implementation bug, because `rppal` didn't implement the transaction part of I2C properly ([#171](https://github.com/golemparts/rppal/issues/171))
 - the Raspberry Pi 3B has a harware limitation with I2c, because it doesn't support clock stretching ([#27](https://github.com/WMT-GmbH/pn532/issues/27))

![I2C clock stretching](/MeloBox/i2c_clock_stretching.png)

 The solution wasn't too hard : I fixed the `Transaction` implementation, and used I2c with the interrupt pin, which means clock stretching is no longer an issue.


## Hardware

I wanted to build something that would go well with my sound amplifier, so I figured I would make a new box in metal. I used 1.5mm thick inox, and a MIG to weld it all together. I made a homemade bender, to get nice rounder corners on the side. 
For the top, I drilled a big hole, so that the RF wave would not be blocked by the metal.

I did burn on raspberry pi because of a shortcircuit, so I learnt to put lots of tape inside to prevent any mistakes.

The last touch was to buy some better-looking buttons, for a more professional look. I used a button with an embedded led, to replace the previous setup.

## Conclusion

I'm really happy.