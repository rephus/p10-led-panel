Additional python scripts for 32x16 panel based on https://github.com/hzeller/rpi-rgb-led-matrix

If needed, use --led-rows=16 --led-multiplexing=8

## Install 

* Clone https://github.com/hzeller/rpi-rgb-led-matrix into your Raspberry PI 

* Connect all the pins to the GPIO accordingly [wiring](https://github.com/hzeller/rpi-rgb-led-matrix/blob/master/wiring.md)

* Run rpi-rgp-led-matrix makefile
```
cd led-matrix/
make
```

* Install python dependencies 

```
sudo apt-get update 
sudo apt-get install python3-dev python3-pillow -y
cd rpi-rgb-led-matrix/bindings/python/samples/ 
make build-python PYTHON=$(which python3)
```

* Copy this files into `rpi-rgb-led-matrix/bindings/python/samples/` folder

* Optional (install redis) 

If you want to run the screen.py script, you need to install redis first 

```
sudo apt-get install redis-server
pip3 install redis
```

* Run `sudo python3 screen.py` 

If you're having problems with the screen resolution, try tweaking the `samplebase.py` default arguments