from flask import Flask, request
import subprocess
import time
import os
import signal
import config

import redis
# https://github.com/andymccurdy/redis-py
r = redis.StrictRedis(host='localhost', port=6379, db=0)
# r.set('foo', 'bar')

app = Flask(__name__)

python_dir = "/home/pi/rpi-rgb-led-matrix/bindings/python/samples"


@app.route("/")
def root():
    action = str.lower(str(request.args.get('action')))

    
    return "Ok!"
 
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8010)