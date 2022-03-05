# Clean resets a tag back to factory-like state
# For Mifare Classic, tag is zero'd and reformatted as Mifare Classic
# For Mifare Ultralight, tags is zero'd and left empty


import time
import binascii

from pn532pi import Pn532, pn532
from pn532pi import Pn532I2c
from pn532pi import Pn532Spi
from pn532pi import Pn532Hsu


PN532_I2C = Pn532I2c(1)
nfc = Pn532(PN532_I2C)


def setup():
    print("NTAG21x R/W")
    print("-------Looking for PN532--------")

    nfc.begin()
    time.sleep(1)
    versiondata = nfc.getFirmwareVersion()
    if not versiondata:
        print("Didn't find PN53x board")
        raise RuntimeError("Didn't find PN53x board")  # halt

    # Got ok data, print it out!
    print("Found chip PN5 {:#x} Firmware ver. {:d}.{:d}".format((versiondata >> 24) & 0xFF, (versiondata >> 16) & 0xFF,
                                                                (versiondata >> 8) & 0xFF))

    # configure board to read RFID tags
    #nfc.SAMConfig()

def loop():
    print("wait for a tag")
    # wait until a tag is present
    tagPresent = False
    while not tagPresent:
        time.sleep(.1)
        tagPresent, uid = nfc.readPassiveTargetID(pn532.PN532_MIFARE_ISO14443A_106KBPS)

    status, buf = nfc.mifareultralight_ReadPage(3)
    capacity = int(buf[2]) * 8
    print("Tag capacity {:d} bytes".format(capacity))

    for i in range(4, int(capacity/4)):
        status, buf = nfc.mifareultralight_ReadPage(i)
        txt = "".join(chr(b) for b in buf[:4])
        print(txt)
        print(binascii.hexlify(buf[:4]))

    # wait until the tag is removed
    while tagPresent:
        time.sleep(.1)
        tagPresent, uid = nfc.readPassiveTargetID(pn532.PN532_MIFARE_ISO14443A_106KBPS)


if __name__ == '__main__':
    setup()
    time.sleep(1)
    while True:
      loop()
