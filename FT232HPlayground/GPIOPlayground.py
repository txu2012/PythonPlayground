import subprocess
import sys

def install(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except Exception as ex:
        print(ex)
        print('Press enter to exit ...')
        input()
        sys.exit(255)

import os
os.environ["BLINKA_FT232H"] = "1"

try:
    import time
    import board
    import digitalio
except ImportError as e:
    install('pyusb')
    install('pyftdi')
    install('adafruit-blinka')

led = digitalio.DigitalInOut(board.C0)
led.direction = digitalio.Direction.OUTPUT

for i in range(20):
    led.value = True
    time.sleep(0.01)
    led.value = False
    time.sleep(0.01)
    
led.value = False