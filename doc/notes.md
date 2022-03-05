PN532 with Arduino : https://how2electronics.com/interfacing-pn532-nfc-rfid-module-with-arduino/#Difference_Between_RFID_038_NFC

A good tutorial of how to setup PN532 with Raspberry Pi : https://blog.stigok.com/2017/10/12/setting-up-a-pn532-nfc-module-on-a-raspberry-pi-using-i2c.html

```shell
i2cdetect -y 1
```

TODOs :
 - led quand detecté
 - boutons next / pause / previous
 - etiquettes sur cassettes
 - meilleure implémentation I2C ?