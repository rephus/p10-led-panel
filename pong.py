#!/usr/bin/env python
from samplebase import SampleBase
from rgbmatrix import graphics
import time
from datetime import datetime


class GraphicsTest(SampleBase):
    def __init__(self, *args, **kwargs):
        super(GraphicsTest, self).__init__(*args, **kwargs)

        
    def run(self):
        canvas = self.matrix.CreateFrameCanvas()
        self.matrix.brightness = 50
        
        font = graphics.Font()
        font.LoadFont("/home/pi/rpi-rgb-led-matrix/fonts/tom-thumb.bdf")

        blue = graphics.Color(0, 0, 255)
        red = graphics.Color(255, 0, 0) 
        green = graphics.Color(0, 255, 0)
        white = graphics.Color(255, 255, 255)

        stick_left = 0 
        stick_right = 0
        ball_x = canvas.width/2
        ball_y = canvas.height/2

        left_needs_to_lose = False 
        right_needs_to_lose = False 

        minute = datetime.now().minute
        hour = datetime.now().hour

        is_left = True
        is_up = True
        while True: 
            canvas.Clear()
            #graphics.DrawLine(canvas, 5, 5, 22, 13, red)
            graphics.DrawLine(canvas, canvas.width/2, 0, canvas.width/2, canvas.height, white)
            
            #graphics.DrawCircle(canvas, 15, 15, 10, green)

            ## Stick logic

            if ball_x < canvas.width/2: 
                if left_needs_to_lose: 
                    pass
                elif ball_y < stick_left: 
                    stick_left -= 1
                else: 
                    stick_left += 1
            else: 
                if right_needs_to_lose: 
                    pass
                elif ball_y < stick_right: 
                    stick_right -= 1
                else: 
                    stick_right += 1

            graphics.DrawLine(canvas, 0, stick_left -2 , 0, stick_left +2, green)
            graphics.DrawLine(canvas, canvas.width-1, stick_right - 2, canvas.width-1, stick_right + 2, red)
            
            ## Ball logic 
            if ball_y < 1 or ball_y > canvas.height-1:
                is_up = not is_up 
            if ball_x < 2: 
                if left_needs_to_lose: 
                    minute =  datetime.now().minute
                    ball_x = canvas.width/2
                    ball_y = canvas.height/2
                    left_needs_to_lose = False
                else: 
                    is_left = not is_left 
            if ball_x > canvas.width-3: 
                if right_needs_to_lose: 
                    hour = datetime.now().hour
                    ball_x = canvas.width/2
                    ball_y = canvas.height/2
                    right_needs_to_lose = False
                else: 
                    is_left = not is_left 

            if is_left: 
                ball_x = ball_x - 1
            else: 
                ball_x = ball_x + 1 

            if is_up: 
                ball_y = ball_y -1 
            else: 
                ball_y = ball_y +1
                
            graphics.DrawCircle(canvas, ball_x, ball_y, 0, white)

            str_time = "{} {}".format(hour, minute)
            graphics.DrawText(canvas, font, 7, 5, blue, str_time)

            if minute != datetime.now().minute: 
                left_needs_to_lose = True
            if hour != datetime.now().hour: 
                right_needs_to_lose = True 
            
            time.sleep(0.1)   # show display for 10 seconds before exit

            canvas = self.matrix.SwapOnVSync(canvas)

# Main function
if __name__ == "__main__":
    graphics_test = GraphicsTest()
    if (not graphics_test.process()):
        graphics_test.print_help()
