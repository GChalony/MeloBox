#include <Wire.h>
#include <PN532_I2C.h>
#include <PN532.h>
#include <NfcAdapter.h>

#define PN532IRQPIN (2)

volatile boolean cState = false;

PN532_I2C pn532_i2c(Wire);
NfcAdapter nfc = NfcAdapter(pn532_i2c);

void cardreading();

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.println("\nHello!");
  nfc.begin();
  uint32_t versiondata = nfc.getFirmwareVersion();
  if (! versiondata) {
    Serial.print("Didn't find PN53x board");
    while (1); // halt
  }
  // Got ok data, print it out!
  Serial.print("Found chip PN5"); Serial.println((versiondata>>24) & 0xFF, HEX); 
  Serial.print("Firmware ver. "); Serial.print((versiondata>>16) & 0xFF, DEC); 
  Serial.print('.'); Serial.println((versiondata>>8) & 0xFF, DEC);
  
  Serial.println(cState);
  attachInterrupt(digitalPinToInterrupt(PN532IRQPIN), cardreading, FALLING);
  //It generates interrupt, I do not really know why?!
  nfc.SAMConfig();
}

void loop() {
  // put your main code here, to run repeatedly:
  if(cState)
  {
    
    Serial.println("Interrupted");
    

    uint8_t success;
    uint8_t uid[] = { 0, 0, 0, 0, 0, 0, 0 };  // Buffer to store the returned UID
    uint8_t uidLength;                        // Length of the UID (4 or 7 bytes depending on ISO14443A card type)
    // Wait for an ISO14443A type cards (Mifare, etc.).  When one is found
    // 'uid' will be populated with the UID, and uidLength will indicate
    // if the uid is 4 bytes (Mifare Classic) or 7 bytes (Mifare Ultralight)
    success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength);
    
    if (success)
    {
      // Display some basic information about the card
      Serial.println("Found an ISO14443A card");
      Serial.print("  UID Length: ");Serial.print(uidLength, DEC);Serial.println(" bytes");
      Serial.print("  UID Value: ");
      nfc.PrintHex(uid, uidLength);
      
    }
    //This must be called or IRQ won't work!
    nfc.startPassiveTargetIDDetection(PN532_MIFARE_ISO14443A);
    cState = false;
    Serial.print("OUT: ");
    Serial.println(cState);
  }
  
}
void cardreading()
{
  
  cState = true;
  
}
