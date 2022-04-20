import glob
import sys
import serial
import time
import socket
from rplidar import RPLidar

#if sys.platform.startswith("linux"):
    #from picamera import PiCamera

class mowerClass:
    def __init__(self) -> None:
        #self.lidar_serial = RPLidar()
        self.arduino_serial = 0
        self.sockC = socket.socket()
    
    def serial_ports(self):
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = 0

        print(ports) 

        for port in ports:
            try:
                if sys.platform.startswith('darwin'):
                    if port.find("usb") != -1:
                        s = serial.Serial(port)
                        s.close()
                        result = 1

                elif sys.platform.startswith('linux'):
                    if(port.find("AMA0") == -1 and port.find("printk") == -1):
                        s = serial.Serial(port)
                        s.close()
                        
                        if port.find("USB1") != -1:
                            self.lidar_serial = RPLidar(port, baudrate=115200, timeout=0.01)
                            print("Connected Lidar.")
                        elif port.find("USB0") != -1:
                            self.arduino_serial = serial.Serial(port, 115200, timeout = 0.3)
                            print("Connected Arduino.")
                        result = 1

                else:
                    s = serial.Serial()
                    s.close()
                    if port.find("COM3") != -1:
                        self.arduino_serial = serial.Serial(port, 115200, timeout = 0.3)
                        self.arduino_serial.reset_input_buffer()
                        print("Connected Arduino.")
                    elif port.find("COM4") != -1:
                        self.lidar_serial = RPLidar(port)
                        self.lidar_serial.reset()
                        self.lidar_serial.clean_input()
                        print("Connected Lidar.")
                    result = 1 
            except:
                pass
        return result

    def takePicture():
        if sys.platform.startswith("linux"):
            camera = PiCamera()
            camera.resolution = (1280, 720)
            time.sleep(2)
            camera.capture("/home/pi/Desktop/intelligenta/Embedded-raspberry/img.jpg")
            camera.close()
        print("Picture taken.")
    
    def readSerial(self):
        #while True:
            for i, scan in enumerate(self.lidar_serial.iter_measures(max_buf_meas=False)):
                if scan[3] != 0 and scan[3] < 300 and (scan[2] <= 45 or scan[2] >= 315):
                    print(scan)
                    print("Angle: %d, Distance: %d" % (scan[2], scan[3]))    
                    self.arduino_serial.write("lidarHit".encode())
                    print("Sent data: lidarHit")
                    self.lidar_serial.stop()
                    while True:
                        read_data = self.arduino_serial.read(0x100)

                        if(len(read_data) >= 3):
                            print("Recieved: " + str(read_data))
                        
                        if str(read_data) == "b'stopped'":
                            #self.takePicture()
                            self.arduino_serial.write("done".encode())
                            print("Sent data: done")

                        elif str(read_data) == "b'done'":
                            self.lidar_serial.start()
                            break

                
