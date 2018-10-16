from samplebase import SampleBase
import time
from datetime import datetime
import config
import random
import math
import sys
# weather

from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image
import requests
import redis
# https://github.com/andymccurdy/redis-py
r = redis.StrictRedis(host='localhost', port=6379, db=0)

class Point:
    """ Point class represents and manipulates x,y coords. """

    def __init__(self, x=0, y=0):
        """ Create a new point at the origin """
        self.x = x
        self.y = y
    def __repr__(self):
        return "({},{})".format(self.x, self.y)


class Screen(SampleBase):
    def __init__(self, *args, **kwargs):
        super(Screen, self).__init__(*args, **kwargs)

        
    def run(self):
        self.canvas = self.matrix.CreateFrameCanvas()

        self.font = graphics.Font()
        self.font.LoadFont("/home/pi/rpi-rgb-led-matrix/fonts/tom-thumb.bdf")
        #self.font.LoadFont("/home/pi/rpi-rgb-led-matrix/fonts/4x6.bdf")

        self.blue = graphics.Color(50, 50, 255)
        self.red = graphics.Color(255, 0, 0)
        self.green = graphics.Color(100, 255, 100)
        self.white = graphics.Color(255, 255, 255)
        self.yellow = graphics.Color(255, 100, 0)

        # Pong initialization
        
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
   
        # Snake start
        self.head = Point()
        self.head.y = 6
        self.tail = [Point(), Point(), Point(), Point(), Point()]
        self.ball = Point()
        self._random_ball(self.ball)
        self.fake_ball = Point()
        self._random_ball(self.fake_ball)

        self.update_time = False
        
        # weather
        
        self.last_weather_request = 0 # cache results for 30 mins
        self.humidity = 0
        self.temperature = 0
        self.home_image = Image.open("/home/pi/rpi-rgb-led-matrix/bindings/python/samples/weather_icons/home8.png")

        #Spotify
        self.spotify_song = ""
        self.changed_screen = time.time()
        self.screen = 0
        
        # Tetris
        
        self.tetrimino = {}
        self.restart_tetris()
        self.shapes = {
            'Z': [[0,0,0,0],
                  [1,1,0,0],
                  [0,1,1,0],
                  [0,0,0,0]],
            'S': [[0,0,0,0],
                  [0,0,1,1],
                  [0,1,1,0],
                  [0,0,0,0]],
            'T': [[0,0,0,0],
                  [1,1,1,0],
                  [0,1,0,0],
                  [0,0,0,0]],
            'I': [[0,1,0,0],
                  [0,1,0,0],
                  [0,1,0,0],
                  [0,1,0,0]],
            'J': [[0,0,0,0],
                  [0,0,1,0],
                  [0,0,1,0],
                  [0,1,1,0]],
            'L': [[0,0,0,0],
                  [0,1,0,0],
                  [0,1,0,0],
                  [0,1,1,0]],
            'O': [[0,0,0,0],
                  [0,1,1,0],
                  [0,1,1,0],
                  [0,0,0,0]],
            
        }
        self.shape_color = {
            'Z': {'r': 0, 'g': 255, 'b': 0},
            'S': {'r': 255, 'g': 0, 'b': 0},
            'T': {'r': 100, 'g': 0, 'b': 100},
            'I': {'r': 0, 'g': 0, 'b': 255},
            'J': {'r': 255, 'g': 0, 'b': 100},
            'L': {'r': 255, 'g': 100, 'b': 0},
            'O': {'r': 100, 'g': 100, 'b': 0},
        }
        #  zip(*original[::-1])
        
    def _change_screen(self, t):
        if self.changed_screen + t < time.time():
            
            # Show spotify song on every screen change,
            # only if the shong has changed.
            self.show_spotify()
            
            self.screen = (self.screen +1) % 4
            self.changed_screen = time.time()
            
            # Change brightness
            now = datetime.now()
            if now.hour >= 22 or now.hour <= 8:
                self.matrix.brightness = 5
            else:
                self.matrix.brightness = 20

                        
    def loop(self):
        while True:
            
            try:
                
                self.canvas.Clear()
            
                if self.screen==0:
                    self._change_screen(30)
                    self.pong_loop()
                elif self.screen==1:
                    self._change_screen(0)
                    self.show_home_weather()
                    self.show_weather()
                elif self.screen==2:
                    self._change_screen(30)
                    self.snake_loop()
                elif self.screen==3:
                    self._change_screen(30)
                    self.tetris()
                else:
                    print("Unexpected screen {}".format(self.screen))
                
                self.canvas = self.matrix.SwapOnVSync(self.canvas)
                
            except Exception as e:
                exc_type, exc_obj, tb = sys.exc_info()

                print("Error, unable to show screen {}: {}".format(tb.tb_lineno, e))
            
            
    def restart_tetris(self):
        print("End tetris game")
        time.sleep(2)

        #reset
        self.blocks = [[0 for x in range(self.matrix.width+2)] for y in range(self.matrix.height+2)]
        # Set limit
        for x in range(self.matrix.width+2):
            self.blocks[16][x] = {'r':255, 'g': 255, 'b': 255}
            
        self.tetrimino = {}
        self.new_tetrimino()
        self.find_tetrimino_hole()
        
    def check_tetris_over(self):
        for x in range(self.matrix.width):
            block = self.blocks[5][x]
            if block:
                self.restart_tetris()
                

    def new_tetrimino(self):
        
        # Draw tetrimino in blocks
        
        if self.tetrimino:
            t = self.tetrimino
            shape = self.shapes[t['shape']]
            for r in range(0, t['rotation']):
                shape = zip(*shape[::-1])
            color = self.shape_color[t['shape']]
            for x in range(4):
                for y in range(4):
                    pixel = shape[y][x]
                    if pixel:
                        self.blocks[t['y']+y-2][t['x']+x-2] = color
 
        # TODO random
        shape = random.choice(['Z', 'S', 'T', 'I', 'O', 'J', 'L'])
        self.tetrimino = {'shape': shape, 'x': self.matrix.width / 2, 'y': 5, 'rotation': 0}
        
        self.find_tetrimino_hole()
        
    def find_tetrimino_hole(self):
        self.next_tetrimino_hole = {'x': random.randint(0, self.matrix.width-1), 'y': self.matrix.height-1}
                    
                    
    def blocked_tetrimino(self, x, y):
        
        try:
            return self.blocks[y][x]
        except:
            print("ERROR blocked tetrimino ", x, y)
            return True
        
    
    def tetris(self):
        
        # Draw existing blocks
        
        for x in range(self.matrix.width):
            for y in range(self.matrix.height):
                b = self.blocks[y][x]
                if b:
                    self.matrix.SetPixel(x, y, b['r'], b['g'], b['b'])
        
        # Current tetrimino
        
        t = self.tetrimino
        
        shape = self.shapes[t['shape']]
        for r in range(0, t['rotation']):
            shape = zip(*shape[::-1])
            
        ## Draw current tetrimino
        color = self.shape_color[t['shape']]
        for x in range(4):
            for y in range(4):
                pixel = shape[y][x]
                if pixel:
                    self.matrix.SetPixel(t['x']+x-2,t['y']+y-2, color['r'], color['g'], color['b'])
    
        t['y'] += 1
        #self.matrix.SetPixel(self.next_tetrimino_hole['x'], self.next_tetrimino_hole['y'], 255, 255, 255) # debug

        # Move tetrimino
        
        if self.next_tetrimino_hole['x'] != t['x']:
            move = 1
            if math.fabs(self.next_tetrimino_hole['x'] - t['x']) > 5:
                move = 2
            if self.next_tetrimino_hole['x'] < t['x']:
                move *= -1
               
            # There is no other tetrimino in the way
            if not self.blocked_tetrimino(t['x'] + move*2, t['y']):
                t['x'] += move
            
        if 2 > random.randint(0,10):
            t['rotation'] = (t['rotation'] + 1 ) % 4

        # Check collission
        
        # Update shape
        shape = self.shapes[t['shape']]
        for r in range(0, t['rotation']):
            shape = zip(*shape[::-1])
        
        check_collision = True
        for x in range(4):
            for y in range(4):
                pixel = shape[y][x]
                if pixel and check_collision:
                    if self.blocked_tetrimino(t['x']+x-2, t['y']+y-1):
                        self.new_tetrimino()
                        self.find_tetrimino_hole()
                        check_collision = False
                        break
                       
        str_time = "{} {}".format( str(self.hour).zfill(2), str(self.minute).zfill(2))
        graphics.DrawText(self.canvas, self.font, 7, 5, self.blue, str_time)

        time.sleep(0.2)

        self.check_tetris_over()

        
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
  
    def show_spotify(self):
        
        # Refresh token
        payload = {'grant_type':'refresh_token', 'refresh_token':config.spotify_refresh_token}
        headers={"Authorization": config.spotify_client_auth}
        r = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=payload)

        # Get current song
        token = r.json()['access_token']
        headers={"Authorization": "Bearer {}".format(token)}
        url = "https://api.spotify.com/v1/me/player"
        response = requests.get(url, headers=headers)

        if response.text:
        
            json = response.json()
            
            current_song = unicode("{} by {}".format(
                json['item']['name'].encode('utf8'),
                json['item']['artists'][0]['name'].encode('utf8')
            ), errors='ignore')
            
            start = time.time()
            pos = self.canvas.width
            if self.spotify_song != current_song:
                self.spotify_song = current_song
                while time.time() < start + 30:
                    self.canvas.Clear()
                    len = graphics.DrawText(self.canvas, self.font, pos, 10, self.green, current_song)
                    pos -= 1
                    if (pos + len < 0):
                        pos = self.canvas.width
        
                    time.sleep(0.05)
                    self.canvas = self.matrix.SwapOnVSync(self.canvas)

    def snake_loop(self):
        
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

        #graphics.DrawLine(canvas, 5, 5, 22, 13, red)
        graphics.DrawCircle(self.canvas, self.head.x, self.head.y, 0, self.red)

        for c, t in enumerate(self.tail):
            color = max(50, 255-30*c)
            self.matrix.SetPixel(t.x,t.y, color, 0, 0)
        
        graphics.DrawCircle(self.canvas, self.ball.x, self.ball.y, 0, self.white)
        #graphics.DrawCircle(self.canvas, self.fake_ball.x, self.fake_ball.y, 0, self.green)

        str_time = "{}:{}".format( str(self.hour).zfill(2), str(self.minute).zfill(2))
        graphics.DrawText(self.canvas, self.font, 7, 5, self.blue, str_time)

        #  Change time
        if self.minute != datetime.now().minute or self.hour != datetime.now().hour:
            self.update_time = True
        
        time.sleep(0.1)   # show display for 10 seconds before exit


    def show_home_weather(self):
        time.sleep(0.01)
        self.canvas = self.matrix.SwapOnVSync(self.canvas)
        self.canvas.Clear()
        
        self.home_image.thumbnail((self.matrix.width, self.matrix.height), Image.ANTIALIAS)
        self.matrix.SetImage(self.home_image.convert('RGB'), 0, 7)

        home_temperature = r.get('temperature').split('.')[0]
        home_humidity = r.get('humidity').split('.')[0]

        graphics.DrawText(self.matrix, self.font, 9, 13, self.yellow, home_temperature)
        graphics.DrawCircle(self.matrix, 18, 9, 1, self.yellow)
        
        graphics.DrawText(self.matrix, self.font, 21, 13, self.blue, "{}%".format(home_humidity))
        
        str_time = "{}:{}".format( str(self.hour).zfill(2), str(self.minute).zfill(2))
        graphics.DrawText(self.matrix, self.font, 7, 5, self.blue, str_time)

        time.sleep(5)
        
        
    def show_weather(self):
        time.sleep(0.01)
        self.canvas = self.matrix.SwapOnVSync(self.canvas)
        self.canvas.Clear()
        
        # Request every 10 mins
        if self.last_weather_request + 600 < time.time():
            
            url = "https://api.darksky.net/forecast/{}/36.65794,-4.5422482?units=si&exclude=hourly,daily".format(config.weather_key)
            
            response = requests.get(url).json()
            self.temperature = str(int(response['currently']['temperature']))
            self.humidity = str(response['currently']['humidity'] * 100).split('.')[0]
            icon = response['currently']['icon']
                    
            self.image = Image.open("/home/pi/rpi-rgb-led-matrix/bindings/python/samples/weather_icons/{}8.png".format(icon))
            
            self.last_weather_request = time.time()

        self.image.thumbnail((self.matrix.width, self.matrix.height), Image.ANTIALIAS)
        self.matrix.SetImage(self.image.convert('RGB'), 0 ,7 )

        #graphics.DrawText(self.matrix, self.font, 20, 6, self.yellow, self.temperature)
        #graphics.DrawCircle(self.matrix, 29, 2, 1, self.yellow)
        
        #graphics.DrawText(self.matrix, self.font, 20, 14, self.blue, "{}%".format(self.humidity))
        
        graphics.DrawText(self.matrix, self.font, 9, 13, self.yellow, self.temperature)
        graphics.DrawCircle(self.matrix, 18, 9, 1, self.yellow)
        
        graphics.DrawText(self.matrix, self.font, 21, 13, self.blue, "{}%".format(self.humidity))
        
        str_time = "{}:{}".format( str(self.hour).zfill(2), str(self.minute).zfill(2))
        graphics.DrawText(self.matrix, self.font, 7, 5, self.blue, str_time)

        time.sleep(5)


    def pong_loop(self):

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

# Main function
if __name__ == "__main__":
    screen = Screen()
    if (not screen.process()):
        screen.print_help()
    else:
        while True:
            screen.loop()
