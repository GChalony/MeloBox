// for I2C Communication
#include <Wire.h>
#include <PN532_I2C.h>
#include <PN532.h>
#include <NfcAdapter.h>


PN532_I2C pn532_i2c(Wire);
NfcAdapter nfc = NfcAdapter(pn532_i2c);

#define INTERRUPT_PIN 2

volatile int state = LOW;

int count = 0;

String tagId = "None";
byte nuidPICC[4];

void setup(void) {
 Serial.begin(115200);
 Serial.println("System initialized");
 nfc.begin();
 //attachInterrupt(digitalPinToInterrupt(INTERRUPT_PIN), receiveNew, CHANGE);
 Serial.println("Ready to read");
}

void loop() {
 readNFC();
 count++;
 Serial.println(count);
 if (state == HIGH) {
  Serial.println("Received interrupt!");
   state = LOW;
 }
 
}

void readNFC() {
 if (nfc.tagPresent()) {
   NfcTag tag = nfc.read();
   tag.print();
   tagId = tag.getUidString();
 }
 delay(5000);
}

void receiveNew() {
  state = HIGH;
}
