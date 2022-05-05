import glob, serial, time, requests, command_variable
from rplidar import RPLidar
from picamera import PiCamera

username = "anniemiken" #this is something that we should receive from mobile as a first startup, maybe use sql database to store so only one time needed
password = "abC!124553"

class mowerClass:
    def __init__(self) -> None:
        self.arduino_serial = 0
        self.manual_mode_enabled = False

        response = 0

        urlSignIn = "http://ec2-54-227-56-79.compute-1.amazonaws.com:8080/auth/sign-in"
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
        
        urlCreateInstance = "http://ec2-54-227-56-79.compute-1.amazonaws.com:8080/mowing-sessions"
        headerCreateInstance = {"Content-Type":"application/json", "Authorization":"Bearer " + self.accessToken}
        dataCreateInstance = {
            "mowerPositions": [[0,0]],
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
        camera.capture("/home/raspberrypi/Desktop/Intelligenta-system/img.jpg")
        camera.close()
        print("Picture taken.")

    def update_position(self):
        urlAddPos = "http://ec2-54-227-56-79.compute-1.amazonaws.com:8080/mowing-sessions"
        headerAddPos = {"Content-Type":"application/json", "Authorization":"Bearer " + self.accessToken}
        dataAddPos = {
            "mowingSessionId": self.mowingSessionID,
            "newMowerPositions": [[1, 1], [2, 2], [3, 3], [4, 4]]   #has to be updated with our own position data
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
        pass
    
    def auto_mode(self):
        self.arduino_serial.write("AM".encode())
        print("Sent data: AM")
        self.lidar_serial.reset()

        for i, scan in enumerate(self.lidar_serial.iter_measures()):
            if scan[3] != 0 and (scan[3] < 300 or scan[3] > 600) and (scan[2] <= 30 or scan[2] >= 330):
                self.lidar_serial.stop()
                print("Angle: %d, Distance: %d" % (scan[2], scan[3]))    

                self.arduino_serial.write("LT".encode())
                print("Sent data: LT")
                
                while True:

                    read_data = self.arduino_serial.read(0x100)

                    if(len(read_data) >= 2):
                        print("Recieved: " + str(read_data))
                    
                    if str(read_data) == "b'LOK'":
                        self.takePicture()
                        self.upload_image()
                        self.lidar_serial.start()
                        break

            if command_variable.command == "MT":
                self.manual_mode_enabled = True
                command_variable.command = 0
                self.lidar_serial.clean_input()
                self.lidar_serial.stop()
                self.lidar_serial.stop_motor()
                break
            
    def manual_mode(self):
        self.arduino_serial.write("MM".encode())
        print("Sent data: MM")

        timeout_time = time.time() + (60 * 2)
        while(1):
            if command_variable.command != 0:
                if command_variable.command == "MT":
                    self.manual_mode_enabled = False
                    command_variable.command = 0
                    break
                self.arduino_serial.write(command_variable.command.encode())
                print("Sent data: " + command_variable.command)
                command_variable.command = 0
                timeout_time = time.time() + (60 * 2)
                
            if timeout_time < time.time():
                self.manual_mode_enabled = False
                break