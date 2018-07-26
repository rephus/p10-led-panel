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

        self.matrix = self.matrix # RGBMatrix(options = options)
        self.matrix.brightness = 50

        url = "https://api.darksky.net/forecast/{}/36.65794,-4.5422482?units=si&exclude=hourly,daily".format(config.weather_key)

        response = requests.get(url).json()
        self.temperature = str(int(response['currently']['temperature']))
        icon = response['currently']['icon']

        self.image = Image.open("/home/pi/rpi-rgb-led-matrix/bindings/python/samples/weather_icons/{}.png".format(icon))

        self.font = graphics.Font()
        self.font.LoadFont("/home/pi/rpi-rgb-led-matrix/fonts/tom-thumb.bdf")

        self.white = graphics.Color(255, 255, 255)

    def loop(self): 
        self.image.thumbnail((self.matrix.width, self.matrix.height), Image.ANTIALIAS)
        self.matrix.SetImage(self.image.convert('RGB'))

        graphics.DrawText(self.matrix, self.font, 20, 8, self.white, self.temperature)
        graphics.DrawCircle(self.matrix, 29, 4, 1, self.white)

        time.sleep(0.1)

# Main function
if __name__ == "__main__":
    graphics_test = Weather()
    if (not graphics_test.process()):
        graphics_test.print_help()
    else: 
        while True: 
            graphics_test.loop()
