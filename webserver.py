from flask import Flask, request
import subprocess
import time
import os
import signal
import config 

app = Flask(__name__)

python_dir = "/home/pi/rpi-rgb-led-matrix/bindings/python/samples"

proc = ""

@app.route("/")
def root():
    global proc
    action = str.lower(str(request.args.get('action')))

    print("Action: {}".format(action))

    if not action: 
        pass 

    if proc:
        print("Killing previous screen {}".format(proc.pid))
        subprocess.Popen("sudo pkill -P {}".format(proc.pid), shell=True)

    if action == "pong" or "unk" in  action : # funk or punk 
        proc = subprocess.Popen("sudo python {}/pong.py --led-rows=16 --led-multiplexing=8".format(python_dir), shell=True, preexec_fn=os.setsid)
    elif action == "weather": 
        proc = subprocess.Popen("sudo python {}/weather.py {}".format(python_dir, config.weather_key), shell=True, preexec_fn=os.setsid)
    elif action == "off" or action == "disable": 
        print("Display off")
    elif action == "volume" or action == "music": 
        proc = subprocess.Popen("sudo /home/pi/rpi-rgb-led-matrix/examples-api-use/demo --led-rows=16 --led-multiplexing=8  -D 9", shell=True, preexec_fn=os.setsid)


    return "Ok!"
 
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8010)