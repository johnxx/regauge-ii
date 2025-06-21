# Re:Gauge II

## Installing

Flash micropython onto your ESP32-S3 board of choice*
```
pip install mpremote
mpremote cp -r lib :
mpremote cp -r faces :
mpremote cp -r sources :
mpremote cp -r hw :
mpremote cp NotoSansDisplay-Regular-96.bin :
mpremote cp main.py
```
Then reset your board and watch some mock data display.

*as long as you chose a WaveShare 1.85" round ESP32-S3
