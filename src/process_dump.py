import os

INPUT = "nfc_fifo"
while True:
    with open(INPUT, "rb") as fifo:
        c = fifo.read()
        start = c.find(b'en')
        end = c.find(b'\xfe')

        uri = c[start + 2: end].decode("utf-8")
        print("Received ", c[start + 2: end])

        if uri.startswith("spotify"):
            os.system(f"spotify play --uri {uri}")
        else:
            print(f"Unrecognized format: {uri}")

