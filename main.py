import time
from mowerClass import mowerClass


mower = mowerClass()


active_serial = mower.serial_ports()
time.sleep(3)

while True:
    if mower.manual_mode_enabled:
        mower.manual_mode()
    else:
        mower.auto_mode()
