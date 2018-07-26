#!/usr/bin/env python
from samplebase import SampleBase

import time
import sys

from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image
import requests 
import config 

class Weather(SampleBase):
    def __init__(self, *args, **kwargs):
        super(Weather, self).__init__(*args, **kwargs)

        
    def run(self):

        matrix = self.matrix # RGBMatrix(options = options)
        matrix.brightness = 50

        url = "https://api.darksky.net/forecast/{}/36.65794,-4.5422482?units=si&exclude=hourly,daily".format(config.weather_key)

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

        while True: 
            time.sleep(1) 

# Main function
if __name__ == "__main__":
    graphics_test = Weather()
    if (not graphics_test.process()):
        graphics_test.print_help()
