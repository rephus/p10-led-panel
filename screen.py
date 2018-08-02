from samplebase import SampleBase
import time
from datetime import datetime
import config
import random

# weather

from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image
import requests

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

        self.blue = graphics.Color(0, 0, 255)
        self.red = graphics.Color(255, 0, 0)
        self.green = graphics.Color(100, 255, 100)
        self.white = graphics.Color(255, 255, 255)

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
        
        #Spotify
        self.spotify_song = ""
        self.changed_screen = time.time()
        self.screen = 0
        
        # Pacman
        self.pacman = Point(x=14, y=6)
        self.fruit = Point(x=14,y=8)
        self.closest_dot = None
        self.collected = 0
        self.blocked_x = None
        self.blocked_y = None
        self.direction = 0  #0 = right, 1= down, 2=left, 3=up

        #self._reset_pacman_dots()
        self._reset_pacman_matrix()
        
        
    def _reset_pacman_matrix(self):
        
        self.collected = 0
        
        self.pactrix = [[0 for x in range(self.matrix.height)] for y in range(self.matrix.width)]
        
        for x in range(0, self.matrix.width) :
            for y in range(0, self.matrix.height):
            
                if x%2 == 0 and y%2 == 0 and\
                    (x < 5 or x > 25 or y < 5 or y > 11) :
                    self.pactrix[x][y] = 1
                    
        # barriers
        
        for x in range(1, 13): self.pactrix[x][5] = 2
        for x in range(17, 30): self.pactrix[x][5] = 2
        for x in range(1, 14): self.pactrix[x][11] = 2
        for x in range(17, 30): self.pactrix[x][11] = 2
        for y in range(5, 11): self.pactrix[5][y] = 2
        for y in range(5, 11): self.pactrix[13][y] = 2
        for y in range(5, 11): self.pactrix[17][y] = 2
        for y in range(5, 11): self.pactrix[25][y] = 2
        
        for x in range(0,5): self.pactrix[x][1] = 2
        for x in range(32-5, 31): self.pactrix[x][1] = 2

        for x in range(2, 10): self.pactrix[x][3] = 2
        for x in range(32-11, 30): self.pactrix[x][3] = 2
        
        for x in range(2, 10): self.pactrix[x][13] = 2
        for x in range(32-11, 30): self.pactrix[x][13] = 2
        
        for x in range(0, 4): self.pactrix[x][9] = 2
        for x in range(32-3, 31): self.pactrix[x][9] = 2
        
        #for y in range(0, 4): self.pactrix[13][y] = 2
        for y in range(0, 4): self.pactrix[17][y] = 2

        for y in range(13, 15): self.pactrix[13][y] = 2

    def _reset_pacman_dots(self):
        self.dots = []
        for y in range(0, self.matrix.height):
            for x in range(0, self.matrix.width) :
            
                if x%2 == 0 and y%2 == 0 and\
                    (x < 5 or x > 25 or y < 5 or y > 11) :
                    self.dots.append(Point(x=x, y=y))
                    
                
    def _change_screen(self, t):
        if self.changed_screen + t < time.time():
            
            # Show spotify song on every screen change,
            # only if the shong has changed.
            self.show_spotify()
            
            self.screen = (self.screen +1) % 3
            self.changed_screen = time.time()
            
            # Change brightness
            now = datetime.now()
            if now.hour >= 22 or now.hour <= 8:
                self.matrix.brightness = 10
            else:
                self.matrix.brightness = 25

                        
    def loop(self):
        while True:
            
            try:
                
                self.canvas.Clear()
                
                #self.pacman_loop()
                
                if self.screen==0:
                    self._change_screen(30)
                    self.pong_loop()
                elif self.screen==1:
                    self._change_screen(0)
                    self.show_weather()
                    time.sleep(5)
                elif self.screen==2:
                    self._change_screen(30)
                    self.snake_loop()
                else:
                    print("Unexpected screen {}".format(self.screen))
                
                self.canvas = self.matrix.SwapOnVSync(self.canvas)
            except Exception as e:
                print("Error, unable to show screen {}".format(e))
            
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
  
        
    def random_move(self):
        if time.time() % 10 > 5:
            return 1
        else:
            return -1
            
    def follow_dot(self):
        #0 = right, 1= down, 2=left, 3=up
        dx, dy = 0,0
        if self.direction == 0:
            dx, dy = 1, 0
        elif self.direction == 1:
            dx, dy = 0, 1
        elif self.direction == 2:
            dx, dy = -1, 0
        elif self.direction == 3:
            dx, dy = 0, -1
            
        if self.pactrix[self.pacman.x +dx][self.pacman.y+ dy] == 2 or\
            self.pacman.x + dx < 0 or self.pacman.x +dx > self.matrix.width -2 or\
            self.pacman.y + dy < 0 or self.pacman.y +dy > self.matrix.height -2:
            self.direction = random.randint(0, 3)
            print("direction ", self.direction)
        else:
            self.pacman.x += dx
            self.pacman.y += dy
            
        if self.pactrix[self.pacman.x][self.pacman.y] == 1:
            self.pactrix[self.pacman.x][self.pacman.y] = 0
            self.collected += 1

        
        
    def old_follow(self):
        
        if self.blocked_x:
            self.pacman.x += self.blocked_x
            self.closest_dot = self._find_closest_dot()
            self.blocked_x = None
        elif self.blocked_y:
            self.pacman.y += self.blocked_y
            self.closest_dot = self._find_closest_dot()
            self.blocked_y = None
            
        elif self.closest_dot:
            #print("pacman ", self.pacman, "closest" , self.closest_dot)
            if self.pacman.x < self.closest_dot.x:
                if self.pactrix[self.pacman.x+1][self.pacman.y] == 2:
                    self.blocked_y = self.random_move()
                else:
                    self.pacman.x += 1
            elif self.pacman.x > self.closest_dot.x:
                if self.pactrix[self.pacman.x-1][self.pacman.y] == 2:
                    self.blocked_y = self.random_move()
                else:
                    self.pacman.x -= 1
            elif self.pacman.y < self.closest_dot.y:
                if self.pactrix[self.pacman.x][self.pacman.y+1] == 2:
                    self.blocked_x =self.random_move()
                else:
                    self.pacman.y += 1
            elif self.pacman.y > self.closest_dot.y:
                if self.pactrix[self.pacman.x][self.pacman.y-1] == 2:
                    self.blocked_x = self.random_move()
                else:
                    self.pacman.y -= 1
            
            if self.pactrix[self.pacman.x][self.pacman.y] == 1:
                self.closest_dot = None
                self.pactrix[self.pacman.x][self.pacman.y] = 0
                self.collected += 1

        else:
            self.closest_dot = self._find_closest_dot()
            print("closest dot " , self.closest_dot)
            """
            for x in range(0, self.matrix.width):
                for y in range(0, self.matrix.height):
                    if self.pactrix[x][y] == 1:
                        self.closest_dot = Point(x=x, y=y)
                        return
                    if self.pactrix[x][y] == 2:
                        break
            """
            
    def _find_closest_dot(self):
 
        x_start = self.pacman.x
        y_start = self.pacman.y
        
        max_x  = 0
        direction = 0 #0 = right, 1= down, 2=left, 3=up
        dx = 0
        dy = 0
        while True:
            print(direction, max_x, dx, dy)
            if direction == 0:
                dx += 1
                if dx > max_x:
                    max_x = dx
                    direction =1
                
            elif direction == 1:
                dy += 1
                if dy == max_x:
                    max_y = dy
                    direction = 2
                    
            elif direction == 2:
                dx -= 1
                if dx == -max_x:
                    direction = 3
                    
            elif direction == 3:
                dy -= 1
                if dy == -max_x:
                    direction = 0
            
            # do
            try:
                if self.pactrix[x_start + dx][y_start + dy] == 1:
                    return Point(x=x_start +dx, y=y_start +dy)
                """if self.pactrix[x_start + dx][y_start + dy] == 2:
                    direction += 1
                    if direction > 3:
                        direction = 0
                        max_x += 1
                    if direction == 1:
                        max_y += 1
                """
            except Exception as e:
                pass
            

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

        str_time = "{} {}".format( str(self.hour).zfill(2), str(self.minute).zfill(2))
        graphics.DrawText(self.canvas, self.font, 7, 5, self.blue, str_time)

        #  Change time
        if self.minute != datetime.now().minute or self.hour != datetime.now().hour:
            self.update_time = True
        
        time.sleep(0.1)   # show display for 10 seconds before exit


    def show_weather(self):
        
        # Request every 30 mins
        if self.last_weather_request + 1800 < time.time():
            
            url = "https://api.darksky.net/forecast/{}/36.65794,-4.5422482?units=si&exclude=hourly,daily".format(config.weather_key)
            
            response = requests.get(url).json()
            self.temperature = str(int(response['currently']['temperature']))
            icon = response['currently']['icon']
                    
            self.image = Image.open("/home/pi/rpi-rgb-led-matrix/bindings/python/samples/weather_icons/{}.png".format(icon))
            
            self.last_weather_request = time.time()
        
        #graphics.DrawText(self.matrix, self.font, 20, 8, self.white, "bleh")
        time.sleep(0.01)
        self.canvas = self.matrix.SwapOnVSync(self.canvas)
        self.canvas.Clear()
        
        self.image.thumbnail((self.matrix.width, self.matrix.height), Image.ANTIALIAS)
        self.matrix.SetImage(self.image.convert('RGB'))

        graphics.DrawText(self.matrix, self.font, 20, 8, self.white, self.temperature)
        graphics.DrawCircle(self.matrix, 29, 4, 1, self.white)
    
    def pacman_loop(self):

        #for dot in self.dots:
        for y in range(0, self.matrix.height):
            for x in range(0, self.matrix.width) :
                d = self.pactrix[x][y]
                if d == 1:
                    self.matrix.SetPixel(x,y, 0, 255, 0)
                if d == 2:
                    self.matrix.SetPixel(x,y, 255, 255, 255)
                    
        self.matrix.SetPixel(self.pacman.x,self.pacman.y, 200, 100, 0)
        self.matrix.SetPixel(self.fruit.x,self.fruit.y, 255, 0, 0)

        self.follow_dot()
        
        str_time = "{} {}".format( str(self.hour).zfill(2), str(self.minute).zfill(2))
        graphics.DrawText(self.canvas, self.font, 6, 11, self.blue, str_time)
        
        time.sleep(0.1)   # show display for 10 seconds before exit

        
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
