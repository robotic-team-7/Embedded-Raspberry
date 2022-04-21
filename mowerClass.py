import subprocess
import glob
import serial
import time
import socket
from rplidar import RPLidar
import requests

#if sys.platform.startswith("linux"):
    #from picamera import PiCamera

class mowerClass:
    def __init__(self) -> None:
        #self.lidar_serial = RPLidar()
        self.arduino_serial = 0
        self.sockC = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        self.sockC.bind(('B8:27:EB:24:DA:F2', 2))
        self.sockC.listen(1)
        self.sockC.settimeout(30)
        self.manual_mode_enabled = True
        #response = requests.get()
    
    def serial_ports(self):
        ports = glob.glob('/dev/tty[A-Za-z]*')

        print(ports) 

        for port in ports:
            try:
                if(port.find("AMA0") == -1 and port.find("printk") == -1):
                    s = serial.Serial(port)
                    s.close()

                    if port.find("USB0") != -1 or port.find("ACM") != -1:
                        self.arduino_serial = serial.Serial(port, baudrate=115200, timeout = 0.3)
                        print("Connected Arduino.")
                    elif port.find("USB1") != -1:
                        self.lidar_port = port
                        self.lidar_serial = RPLidar(port)
                        print("Connected Lidar.")
            except:
                pass

    def takePicture(void):
        camera = PiCamera()
        camera.resolution = (1280, 720)
        time.sleep(2)
        camera.capture("/home/pi/Desktop/Intelligenta-system/img.jpg")
        camera.close()
        print("Picture taken.")
    
    def auto_mode(self):
        self.arduino_serial.write("AM".encode())
        print("Sent data: AM")
        self.lidar_serial.reset()

        for i, scan in enumerate(self.lidar_serial.iter_measures()):
            if scan[3] != 0 and (scan[3] < 300 or scan[3] > 600)and (scan[2] <= 30 or scan[2] >= 330):
                self.lidar_serial.stop()
                print("Angle: %d, Distance: %d" % (scan[2], scan[3]))    
            
                self.arduino_serial.write("LT".encode())
                print("Sent data: LT")

                while True:

                    read_data = self.arduino_serial.read(0x100)

                    if(len(read_data) >= 2):
                        print("Recieved: " + str(read_data))
                    
                    if str(read_data) == "b'LOK'":
                        #self.takePicture()
                        self.lidar_serial.start()
                        break


    def manual_mode(self):
        self.arduino_serial.write("MM".encode())
        print("Sent data: MM")
        subprocess.call(['sudo', 'hciconfig', 'hci0', 'piscan'])
        print("Waiting for connection.")

        try:
            client, address = self.sockC.accept()
        except:
            print("No client tried to connect.")
            self.manual_mode_enabled = False
            subprocess.call(['sudo', 'hciconfig', 'hci0', 'piscanoff'])
            return

        subprocess.call(['sudo', 'hciconfig', 'hci0', 'piscanoff'])
        print("Connected to address: " + address[0] + " Port: " + str(address[1]))

        while(1):
            try:
                data = client.recv(1024)
                if data:
                    print("Sent data: " + str(data)[2:len(str(data))-1])
                    self.arduino_serial.write(str(data)[2:len(str(data))-1].encode())
                    client.send(data)
                else:
                    print("No data available.")
            except:
                print("Closing socket. Changing mode to auto.")
                client.close()
                self.manual_mode_enabled = False
                break
            
