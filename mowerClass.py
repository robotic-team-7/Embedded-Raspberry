import glob
import time
import requests
import serial
from picamera import PiCamera
from rplidar import RPLidar
import command_variable

username = "anniemiken"
password = "abC!124553"

url = 'ec2-54-227-56-79.compute-1.amazonaws.com'
class mowerClass:
    def __init__(self) -> None:
        self.arduino_serial = 0
        self.manual_mode_enabled = False

        response = 0
        self.positions = []
        while True:
            try:
                urlSignIn = "http://{}:8080/auth/sign-in".format(url)
                headerSignIn = {"Content-Type":"application/json"}
                dataSignIn = {
                    "username": username,
                    "password": password
                }
                print("Requesting data.")
                try:
                    response = requests.post(urlSignIn, headers= headerSignIn, json= dataSignIn, timeout= 5)    #Authorization
                except requests.exceptions.Timeout:
                    print("No data.")
                else:
                    print("Got data.")
                    print(response.status_code)
                    self.accessToken = response.json()['accessToken']
                    break
            except:
                time.sleep(2)
                pass
        
        urlCreateInstance = "http://{}:8080/mowing-sessions".format(url)
        headerCreateInstance = {"Content-Type":"application/json", "Authorization":"Bearer " + self.accessToken}
        dataCreateInstance = {
            "mowerPositions": [[0.0, 0.0]],
            "mowerId": "abc123"
        }
        print("Requesting data.")
        try:
            response = requests.post(urlCreateInstance, headers= headerCreateInstance, json= dataCreateInstance, timeout= 5)    #Create session
        except requests.exceptions.Timeout:
            print("No data.")
        else:
            print("Got data.")
            print(response.status_code)
            self.mowingSessionID = response.json()
    
    def serial_ports(self):
        ports = glob.glob('/dev/tty[A-Za-z]*')

        print(ports) 

        for port in ports:
            try:
                if(port.find("AMA0") == -1 and port.find("printk") == -1 and port.find("USB0") == -1):
                    s = serial.Serial(port)
                    s.close()

                    if port.find("USB1") != -1:
                        self.arduino_serial = serial.Serial(port, baudrate=115200, timeout=0.3)
                        print("Connected Arduino.")
            except:
                pass

    def takePicture(self):
        camera = PiCamera()
        camera.resolution = (1280, 720)
        time.sleep(1)
        camera.capture("/home/raspberrypi/Desktop/Intelligenta-system/img.jpeg", format="jpeg")
        camera.close()
        print("Picture taken.")


    def update_position(self):
        urlAddPos = "http://{}:8080/mowing-sessions".format(url)
        headerAddPos = {"Content-Type":"application/json", "Authorization":"Bearer " + self.accessToken}
        
        print("Updating positions.")

        dataAddPos = {
            "mowingSessionId": self.mowingSessionID,
            "newMowerPositions": self.positions   #has to be updated with our own position data
        }

        try:
            response = requests.put(urlAddPos, headers= headerAddPos, json= dataAddPos, timeout= 5)
        except requests.exceptions.Timeout:
            print("No data.")
        else:
            print("Got data.")
            print(response.status_code)
            print(response.json())
    
    def upload_image(self):
        urlUploadImage = "http://{}:8080/obstacle/add".format(url)
        dataUploadImage = {
            "mowingSessionId": self.mowingSessionID,
            "obstaclePosition": [self.positions[len(self.positions)-1][0], self.positions[len(self.positions)-1][1]]
            }
        myFiles = [
            ('obstacleImage', ("img.jpeg",open("/home/raspberrypi/Desktop/Intelligenta-system/img.jpeg", 'rb'), 'image/jpeg'))
        ]
        headerUploadImage = { 
            "Authorization":"Bearer " + self.accessToken
            }
        
        print("Uploading image.")
        try:
            response = requests.request("POST", urlUploadImage, headers= headerUploadImage, data= dataUploadImage, files = myFiles, timeout= 5)
        except requests.exceptions.Timeout:
            print("No data.")
        else:
            print("Got data.")
            print(response.status_code)
            print(response.json())
    
    def auto_mode(self):
        self.arduino_serial.write("AM".encode())
        print("Sent data: AM")
        time.sleep(0.5)
        command_variable.lidar_hit = False
        sent_picture = False

        while True:
            if command_variable.command == "MT":
                self.manual_mode_enabled = True
                command_variable.command = ""
                break

            if self.arduino_serial.in_waiting:

                coordinates = self.arduino_serial.readline()[:-1]

                tempVar = coordinates.decode('UTF-8').split(",")
                for i in range(2):
                    tempVar[i] = float(tempVar[i])

                self.positions.append(tempVar)

                if len(self.positions) >= 4:
                    self.update_position()
                    print(self.positions)
                    self.positions.clear()

            
            if command_variable.lidar_hit:
                self.arduino_serial.write("LT".encode())
                print("Sent data: LT")
    
                while True:

                    all_read_data = self.arduino_serial.read(0x100).decode('UTF-8').split("\n")

                    for read_data in all_read_data:
                        if(len(read_data) >= 2):
                            print("Recieved: " + str(read_data))
                        
                        if str(read_data) == "LOK":
                            if command_variable.lidar_stup == False:
                                self.takePicture()
                                self.arduino_serial.write("PT".encode())
                                print("Sent data: PT")
                                self.upload_image()
                            sent_picture = True
                        elif len(read_data) >= 6:
                            tempVar = coordinates.decode('UTF-8').split(",")
                            for i in range(2):
                                tempVar[i] = float(tempVar[i])
                            self.positions.append(tempVar)
                            print("Added latest pos.")

                    if sent_picture:
                        sent_picture = False
                        break
        
                #time.sleep(0.2)
                command_variable.lidar_hit = False
                command_variable.lidar_stup = False
          
    def manual_mode(self):
        self.arduino_serial.write("MM".encode())
        print("Sent data: MM")
        time.sleep(0.5)

        timeout_time = time.time() + (60 * 2)

        while(1):
            if command_variable.command != "":
                if command_variable.command == "MT":
                    self.manual_mode_enabled = False
                    command_variable.command = ""
                    break
                self.arduino_serial.write(command_variable.command.encode())
                print("Sent data: " + command_variable.command)
                command_variable.command = ""
                timeout_time = time.time() + (60 * 2)
                
            if timeout_time < time.time():
                self.manual_mode_enabled = False
                break

            if self.arduino_serial.in_waiting:

                coordinates = self.arduino_serial.readline()[:-1]

                tempVar = coordinates.decode('UTF-8').split(",")
                for i in range(2):
                    tempVar[i] = float(tempVar[i])

                self.positions.append(tempVar)

                if len(self.positions) >= 4:
                    self.update_position()
                    print(self.positions)
                    self.positions.clear()

def lidarSerial():
    ports = glob.glob('/dev/tty[A-Za-z]*')
    lidar_serial = 0

    for port in ports:
        try:
            if(port.find("AMA0") == -1 and port.find("printk") == -1):
                s = serial.Serial(port)
                s.close()

                if port.find("USB0") != -1:
                    lidar_serial = RPLidar(port)
                    print("Connected Lidar.")
        except:
            pass

    lidar_serial.reset()
   
    while True:
        for i, scan in enumerate(lidar_serial.iter_measures()):
            if command_variable.lidar_hit == False:
                #if scan[3] != 0 and (scan[3] < 300 or scan[3] > 600) and (scan[2] <= 30 or scan[2] >= 330):
                if scan[3] != 0 and scan[3] < 300 and (scan[2] <= 30 or scan[2] >= 330):
                    command_variable.lidar_hit = True
                    #if scan[3] > 600:
                        #command_variable.lidar_stup = True
