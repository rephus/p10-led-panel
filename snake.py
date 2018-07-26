#!/usr/bin/env python
from samplebase import SampleBase
from rgbmatrix import graphics
import time
from datetime import datetime
import random


class Point:
    """ Point class represents and manipulates x,y coords. """

    def __init__(self):
        """ Create a new point at the origin """
        self.x = 0
        self.y = 0
    def __repr__(self):
        return "({},{})".format(self.x, self.y)

class Snake(SampleBase):
    def __init__(self, *args, **kwargs):
        super(Snake, self).__init__(*args, **kwargs)

        
    def run(self):
        self.canvas = self.matrix.CreateFrameCanvas()
        self.matrix.brightness = 50
        
        self.font = graphics.Font()
        self.font.LoadFont("/home/pi/rpi-rgb-led-matrix/fonts/4x6.bdf")

        self.blue = graphics.Color(0, 0, 255)
        self.red = graphics.Color(255, 0, 0) 
        self.green = graphics.Color(0, 255, 0)
        self.white = graphics.Color(255, 255, 255)

        self.head = Point() 
        self.head.y = 6
        self.tail = [Point(), Point(), Point(), Point(), Point()]
        self.ball = Point()
        self._random_ball(self.ball)
        self.fake_ball = Point()
        self._random_ball(self.fake_ball)

        self.minute = datetime.now().minute
        self.hour = datetime.now().hour
    
        self.update_time = False 
        
    def _random_ball(self, ball): 
        ball.x = random.randint(0, self.matrix.width-1)
        ball.y = random.randint(6, self.matrix.height-1)

    def follow(self, ball): 
        ## head logic 
        if self.head.x < ball.x: 
            self.head.x += 1
        elif self.head.x > ball.x: 
            self.head.x -= 1
        elif self.head.y < ball.y: 
            self.head.y += 1
        elif self.head.y > ball.y: 
            self.head.y -= 1
        elif self.head.x == ball.x and self.head.y == ball.y: 
            if self.update_time: 
                ## Collect 
                self.update_time = False
                self.minute = datetime.now().minute
                self.hour = datetime.now().hour
                self._random_ball(self.ball)
                if (len(self.tail) < 9):
                    self.tail.append(Point())
            else: 
                self._random_ball(self.fake_ball)

    def loop(self): 
        
        previous_head = Point() 
        previous_head.x = self.head.x
        previous_head.y = self.head.y 
        previous_head_temp = Point()

        ## head logic 
        if self.update_time: 
            self.follow(self.ball)
        else: 
            self.follow(self.fake_ball)

        for t in self.tail: 
            previous_head_temp.x = t.x
            previous_head_temp.y = t.y

            t.x = previous_head.x
            t.y = previous_head.y  
            previous_head.x = previous_head_temp.x 
            previous_head.y = previous_head_temp.y

        # Drawing 

        self.canvas.Clear()
        #graphics.DrawLine(canvas, 5, 5, 22, 13, red)        
        graphics.DrawCircle(self.canvas, self.head.x, self.head.y, 0, self.red)

        for c, t in enumerate(self.tail): 
            color = max(50, 255-30*c)
            self.matrix.SetPixel(t.x,t.y, color, 0, 0)
        
        graphics.DrawCircle(self.canvas, self.ball.x, self.ball.y, 0, self.white)
        #graphics.DrawCircle(self.canvas, self.fake_ball.x, self.fake_ball.y, 0, self.green)

        str_time = "{} {}".format( str(self.hour).zfill(2), str(self.minute).zfill(2))
        graphics.DrawText(self.canvas, self.font, 7, 5, self.blue, str_time)

        #  Change time 
        if self.minute != datetime.now().minute or self.hour != datetime.now().hour: 
            self.update_time = True
        
        time.sleep(0.1)   # show display for 10 seconds before exit

        self.canvas = self.matrix.SwapOnVSync(self.canvas)

# Main function
if __name__ == "__main__":
    graphics_test = Snake()
    if (not graphics_test.process()):
        graphics_test.print_help()
    else: 
        while True: 
            graphics_test.loop()
