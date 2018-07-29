
import requests
from samplebase import SampleBase
from rgbmatrix import graphics
import time
import config

class Spotify(SampleBase):
    def __init__(self, *args, **kwargs):
        super(Spotify, self).__init__(*args, **kwargs)

    def run(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()

        font.LoadFont("../../../fonts/tom-thumb.bdf")
        textColor = graphics.Color(100, 255, 100)
        pos = offscreen_canvas.width
        
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
            my_text = "{} by {}".format(
                json['item']['name'],
                json['item']['artists'][0]['name']
            )
        else:
            print("Unable to get song info", response.text)
            my_text = "No song is playing"
            
        while True:
            
            offscreen_canvas.Clear()
            len = graphics.DrawText(offscreen_canvas, font, pos, 10, textColor, my_text)
            pos -= 1
            if (pos + len < 0):
                pos = offscreen_canvas.width

            time.sleep(0.05)
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
        

# Main function
if __name__ == "__main__":
    run_text = Spotify()
    if (not run_text.process()):
        run_text.print_help()
