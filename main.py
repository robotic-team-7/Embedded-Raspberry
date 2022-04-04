import serial
import sys
import glob

from camera import takePicture

def serial_ports():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = 0
    for port in ports:
        try:
            if port.find("usb") != -1 and sys.platform.startswith('darwin'):
                s = serial.Serial(port)
                s.close()
                result = port
            else:
                s = serial.Serial(port)
                s.close()
                result = port
        except:
            pass
    return result

while True:
    activeserial = serial_ports()

    if(activeserial != 0):
        print(activeserial)
        ser = serial.Serial(activeserial, 9600, timeout=0.01)


        while True:
            read_data = ser.read(0x100)
            if(len(read_data) >= 3):
                print(read_data)
            if str(read_data) == "b'hit'":
                messageToSend = "done"
                takePicture()
                print(messageToSend)
                ser.write(messageToSend.encode())
                print("sent data")
            else:
                pass
