import binascii
from pn532pi import Pn532, pn532
from pn532pi import Pn532I2c
import time

FIFO_NAME = "nfc_fifo"

PN532_I2C = Pn532I2c(1)  # Change to use other I2C pins
nfc = Pn532(PN532_I2C)

def describeVersion(versiondata):
    print("Found chip PN5 {:#x} Firmware ver. {:d}.{:d}".format((versiondata >> 24) & 0xFF, (versiondata >> 16) & 0xFF,
                                                                (versiondata >> 8) & 0xFF))


def setupNFC():
    print("setup")
    nfc.begin()
    version = None
    for i in range(5):
        print(f"reading version {i}")
        version = nfc.getFirmwareVersion()
        if version != None:
            break
    
    if version is None:
        print("Couldn't get firmware info after 5 retries")
        return False

    describeVersion(version)

    nfc.setPassiveActivationRetries(0xFF)
    
    return True


def readNFC():
    print("Reading tag")
    tagPresent = False
    while not tagPresent:
        time.sleep(.1)
        
        tagPresent, uid = nfc.readPassiveTargetID(pn532.PN532_MIFARE_ISO14443A_106KBPS)
        # except OSError:
        #     print("Got OSError, retrying")

    status, buf = nfc.mifareultralight_ReadPage(3)
    capacity = int(buf[2]) * 8
    print("Tag capacity {:d} bytes".format(capacity))

    text_content = ""
    for i in range(4, int(capacity/4)):
        status, buf = nfc.mifareultralight_ReadPage(i)
        txt = "".join(chr(b) for b in buf[:4])
        text_content += txt
        print(txt)
        print(binascii.hexlify(buf[:4]))

    return text_content
    

def waitForTagRemoved():
    tagPresent = True
    while tagPresent:
        time.sleep(.1)
        tagPresent, uid = nfc.readPassiveTargetID(pn532.PN532_MIFARE_ISO14443A_106KBPS)

    print("Tag removed")
    

if __name__ == "__main__":
    print("Starting...")
    if setupNFC():
        with open(FIFO_NAME, "w") as fifo:
            while True:
                content = readNFC()
                fifo.write(content)
                waitForTagRemoved()
