import subprocess
from time import sleep

class NFCReader:
    CARD_DUMP = "card.mfd"
    tag_connected = False

    def wait_for_tag(self):
        while not self.is_tag_connected():
            sleep(0.1)
        self.tag_connected = True

    def read_tag(self):
        with open(NFCReader.CARD_DUMP, "rb") as f:
            data = f.read()
            start = data.find(b'en')
            end = data.find(b'\xfe')
            try:
                uri = data[start + 2: end].decode("utf-8")
                print("Received ", data[start + 2: end])

                # Support shorten URI
                if uri.startswith("spt:"):
                    uri = uri.replace("spt:", "spotify:")
                if uri.startswith("spotify:"):
                    return uri
                else:
                    print("Warning: URI format not recognized:", uri)

            except:
                return None

    def wait_for_tag_removed(self):
        while self.is_tag_connected():
            sleep(0.1)
        print("Tag removed")
        self.tag_connected = False
    

    def is_tag_connected(self):
        return self._call_nfc_mfutltralight().returncode == 0

    def _call_nfc_mfutltralight(self):
        return subprocess.run(["nfc-mfultralight", "r", NFCReader.CARD_DUMP], 
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)