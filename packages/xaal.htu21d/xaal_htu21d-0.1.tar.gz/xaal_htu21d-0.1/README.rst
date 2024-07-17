
xAAL support for HTU21D sensors
===============================
HTU21D combine a temperature and humidity sensors in a single package.
You can find some breakboard for less than 5$ on ebay. 

This program simply export the temperature & humidity on the xAAL bus.

We tested this on a Raspberry PI 3, but it should work with any device
that has a I2C bus. 

Original HTU21D Python module come from the weather station project:
https://github.com/raspberrypi/weather-station/blob/master/HTU21D.py

