import threading
import time
from command_variable import initialize
from BLE_BLUEZ.BLE_funcs import BLE
from mowerClass import mowerClass, lidar_serial

mower = mowerClass()
initialize() #initializing global variable for commands sent with BLE

bt_thread = threading.Thread(target=BLE)
bt_thread.start()

lidar = threading.Thread(target=lidar_serial)
lidar.start()

time.sleep(4)

mower.serial_ports()
time.sleep(2)

while True:
    if mower.manual_mode_enabled:
        mower.manual_mode()
    else:
        mower.auto_mode()
