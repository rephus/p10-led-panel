#!/usr/bin/env python
import time
import sys

from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image
import requests 

darksky_key = sys.argv[1]


# Configuration for the matrix
options = RGBMatrixOptions()
options.rows = 16
options.chain_length = 1
options.parallel = 1
options.multiplexing = 8
options.hardware_mapping = 'regular'  # If you have an Adafruit HAT: 'adafruit-hat'

matrix = RGBMatrix(options = options)
matrix.brightness = 50

url = "https://api.darksky.net/forecast/{}/36.65794,-4.5422482?units=si&exclude=hourly,daily".format(darksky_key)

response = requests.get(url).json()
temperature = str(int(response['currently']['temperature']))
icon = response['currently']['icon']

image = Image.open("/home/pi/rpi-rgb-led-matrix/bindings/python/samples/weather_icons/{}.png".format(icon))
image.thumbnail((matrix.width, matrix.height), Image.ANTIALIAS)
matrix.SetImage(image.convert('RGB'))

font = graphics.Font()
font.LoadFont("/home/pi/rpi-rgb-led-matrix/fonts/tom-thumb.bdf")

white = graphics.Color(255, 255, 255)
graphics.DrawText(matrix, font, 20, 8, white, temperature)
graphics.DrawCircle(matrix, 29, 4, 1, white)

try:
    print("Press CTRL-C to stop.")
    while True:
        time.sleep(100)
except KeyboardInterrupt:
    sys.exit(0)
