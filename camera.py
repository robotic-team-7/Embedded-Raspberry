import time
import sys

if sys.platform.startswith("linux"):
    from picamera import PiCamera

def takePicture():
    if sys.platform.startswith("linux"):
        camera = PiCamera()
        camera.resolution = (1280, 720)
        time.sleep(2)
        camera.capture("/home/pi/Desktop/intelligenta/Embedded-raspberry/img.jpg")
        camera.close()
    print("Picture taken.")