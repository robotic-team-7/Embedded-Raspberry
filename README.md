# The mower: Raspberry

## Technology
The Raspberry incorperates some open source libraries, provided by Python and/or installed libraries, in order to work properly:

- [Threading](https://github.com/python/cpython/blob/3.10/Lib/threading.py)
- [Time]()
- [Glob](https://github.com/python/cpython/blob/3.10/Lib/glob.py)
- [Requests](https://github.com/psf/requests)
- [Serial](https://github.com/pyserial/pyserial)
- [Picamera](https://github.com/waveform80/picamera)
- [Rplidar](https://github.com/Roboticia/RPLidar)

The BLE advertising server (BLE_funcs.py file) for the Raspberry PI was created from an example that can be found [here](https://scribles.net/creating-ble-gatt-server-uart-service-on-raspberry-pi/), this code takes advantage of BLUEZ own advertisement and gatt server example. The code was modified to a small degreee to fit with the rest of the code as intended.

For the program to start up with the boot of the Raspberry PI the Rplidar library had to be moved to the work folder.

## Serial communication messages
| During state      | Message    | Incoming/outgoing | Description |
| -----------       | -------    | -------           | ----------- |
| Any               | AM         | Outgoing          | Enter auto mode |
| Any               | MM         | Outgoing          | Enter manual mode |
| Any               | X,Y        | Incoming          | Coordinates of the robot's current position. Sent every 250 milliseconds and/or when an obstacle appears. Calculated as cm from start position |
| Manual mode       | MS         | Outgoing          | Manual stop |
| Manual mode       | MF         | Outgoing          | Manual forward |
| Manual mode       | MB         | Outgoing          | Manual backwards |
| Manual mode       | ML         | Outgoing          | Manual left |
| Manual mode       | MR         | Outgoing          | Manual right |
| Auto mode         | LT         | Outgoing          | Lidar triggered |
| Auto mode         | LOK        | Incoming          | Arduino has reacted to lidar triggered, Arduino is now waiting for Raspberry Pi to take picture |
| Auto mode         | PT         | Outgoing          | Picture taken after lidar triggered |
