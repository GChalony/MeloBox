import subprocess
from time import sleep

class NFCReader:
    CARD_DUMP = "card.mfd"
    def wait_for_tag(self):
        while self._call_nfc_mfutltralight().returncode != 0:
            sleep(0.1)

    def read_tag(self):
        with open(NFCReader.CARD_DUMP, "rb") as f:
            data = f.read()
            start = data.find(b'en')
            end = data.find(b'\xfe')

            uri = data[start + 2: end].decode("utf-8")
            print("Received ", data[start + 2: end])

            if uri.startswith("spotify:"):
                return uri
            else:
                print("Warning: URI format not recognized:", uri)


    def wait_for_tag_removed(self):
        while self._call_nfc_mfutltralight().returncode == 0:
            sleep(0.1)
        
    def _call_nfc_mfutltralight(self):
        return subprocess.run(["nfc-mfultralight", "r", NFCReader.CARD_DUMP], 
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)