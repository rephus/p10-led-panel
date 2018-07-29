#!/usr/bin/env python
from samplebase import SampleBase
from rgbmatrix import graphics
import time
from datetime import datetime


class Pong(SampleBase):
    def __init__(self, *args, **kwargs):
        super(Pong, self).__init__(*args, **kwargs)

        
    def run(self):
        self.canvas = self.matrix.CreateFrameCanvas()

        self.font = graphics.Font()
        self.font.LoadFont("/home/pi/rpi-rgb-led-matrix/fonts/tom-thumb.bdf")

        self.blue = graphics.Color(0, 0, 255)
        self.red = graphics.Color(255, 0, 0)
        self.green = graphics.Color(0, 255, 0)
        self.white = graphics.Color(255, 255, 255)

        self.stick_left = 0
        self.stick_right = 0
        self.ball_x = self.canvas.width/2
        self.ball_y = self.canvas.height/2

        self.left_needs_to_lose = False
        self.right_needs_to_lose = False

        self.minute = datetime.now().minute
        self.hour = datetime.now().hour

        self.is_left = True
        self.is_up = True
    
    def loop(self):

        ## Stick logic
        if self.ball_x < self.canvas.width/2:
            if self.left_needs_to_lose:
                pass
            elif self.ball_y < self.stick_left:
                self.stick_left -= 1
            else:
                self.stick_left += 1
        else:
            if self.right_needs_to_lose:
                pass
            elif self.ball_y < self.stick_right:
                self.stick_right -= 1
            else:
                self.stick_right += 1

        ## Ball logic
        if self.ball_y < 1 or self.ball_y > self.canvas.height-1:
            self.is_up = not self.is_up
        if self.ball_x < 2:
            if self.left_needs_to_lose:
                self.minute =  datetime.now().minute
                self.ball_x = self.canvas.width/2
                self.ball_y = self.canvas.height/2
                self.left_needs_to_lose = False
            else:
                self.is_left = not self.is_left
        if self.ball_x > self.canvas.width-3:
            if self.right_needs_to_lose:
                self.hour = datetime.now().hour
                self.ball_x = self.canvas.width/2
                self.ball_y = self.canvas.height/2
                self.right_needs_to_lose = False
            else:
                self.is_left = not self.is_left

        if self.is_left:
            self.ball_x = self.ball_x - 1
        else:
            self.ball_x = self.ball_x + 1

        if self.is_up:
            self.ball_y = self.ball_y -1
        else:
            self.ball_y = self.ball_y +1

        # Drawing

        self.canvas.Clear()
        #graphics.DrawLine(canvas, 5, 5, 22, 13, red)
        graphics.DrawLine(self.canvas, self.canvas.width/2, 0, self.canvas.width/2, self.canvas.height, self.white)
        
        graphics.DrawLine(self.canvas, 0, self.stick_left -2 , 0, self.stick_left +2, self.green)
        graphics.DrawLine(self.canvas, self.canvas.width-1, self.stick_right - 2, self.canvas.width-1, self.stick_right + 2, self.red)

        graphics.DrawCircle(self.canvas, self.ball_x, self.ball_y, 0, self.white)

        str_time = "{} {}".format( str(self.hour).zfill(2), str(self.minute).zfill(2))
        graphics.DrawText(self.canvas, self.font, 7, 5, self.blue, str_time)

        #  Change time
        if self.minute != datetime.now().minute:
            self.left_needs_to_lose = True
        if self.hour != datetime.now().hour:
            self.right_needs_to_lose = True
        
        time.sleep(0.1)   # show display for 10 seconds before exit

        self.canvas = self.matrix.SwapOnVSync(self.canvas)

# Main function
if __name__ == "__main__":
    graphics_test = Pong()
    if (not graphics_test.process()):
        graphics_test.print_help()
    else:
        while True:
            graphics_test.loop()
