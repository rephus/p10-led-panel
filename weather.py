#!/usr/bin/env python
import time
import sys

from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image

image = Image.open("sun.png")

# Configuration for the matrix
options = RGBMatrixOptions()
options.rows = 16
options.chain_length = 1
options.parallel = 1
options.multiplexing = 8
options.hardware_mapping = 'regular'  # If you have an Adafruit HAT: 'adafruit-hat'

matrix = RGBMatrix(options = options)

# Make image fit our screen.
image.thumbnail((matrix.width, matrix.height), Image.ANTIALIAS)

matrix.SetImage(image.convert('RGB'))

font = graphics.Font()
font.LoadFont("../../../fonts/tom-thumb.bdf")

white = graphics.Color(255, 255, 255)
graphics.DrawText(matrix, font, 20, 8, white, "32")
graphics.DrawCircle(matrix, 29, 4, 1, white)



try:
    print("Press CTRL-C to stop.")
    while True:
        time.sleep(100)
except KeyboardInterrupt:
    sys.exit(0)
