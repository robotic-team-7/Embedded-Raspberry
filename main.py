import glob
import sys
import time
import serial

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

    print(ports) 

    for port in ports:
        try:
            if sys.platform.startswith('darwin'):
                if port.find("usb") != -1:
                    s = serial.Serial(port)
                    s.close()
                    result = port
            elif sys.platform.startswith('linux'):
                if(port.find("AMA0") == -1 and port.find("printk") == -1):
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
            try:
                read_data = ser.read(0x100)
                if(len(read_data) >= 3):
                    print(read_data)
                if str(read_data) == "b'hit'":
                    messageToSend = "done"
                    takePicture()
                    print(messageToSend)
                    ser.write(messageToSend.encode())
                    print("sent data")
            except:
                activeserial = 0
                break
    time.sleep(0.5)
