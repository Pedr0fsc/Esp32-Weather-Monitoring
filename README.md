# Esp32-Weather-Monitoring

A MicroPython aplication using the famous Esp32 as the microcontroller, the weather station consists into 2 sensors, BMP280 and DHT11, and a IPS 240x240 display. The project has visual display not only with the eletronic components, but also in your phone, with a webserver with auto-refresh for see real-time datas from the sensors.

### Essential Terminal Commands

* Connect to board / Enter REPL:
`mpremote connect (your COM port)`
* Upload files to board:
`mpremote connect (your COM port) cp (file_name.py) :`
* Run files from IDE or from board (Check package.json):
`mpremote connect (your COM port) run (file_name.py)`
* List files from the board:
`mpremote connect (your COM port) fs ls`
* Delete files from the board:
`mpremote connect (your COM port) fs rm :(file_name.py)`