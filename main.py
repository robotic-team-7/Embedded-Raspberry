import time
from mowerClass import mowerClass


mower = mowerClass()

while True:
    active_serial = mower.serial_ports()
    #time.sleep(3)
    
    while active_serial:
        read_data = mower.readSerial()
    
    active_serial = 0

    time.sleep(0.5)
