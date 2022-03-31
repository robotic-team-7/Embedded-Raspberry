import serial
import sys
import glob

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
        except (OSError, serial.SerialException):
            pass
    return result

activeserial = serial_ports()
print(activeserial)
ser = serial.Serial(activeserial, 9600, timeout=0.01)


while True:
    read_data = ser.read(0x100)
    if(len(read_data) >= 3):
        print(read_data)
    if str(read_data) == "b'hit'":
        messageToSend = "done"
        print(messageToSend)
        ser.write(messageToSend.encode())
    else:
        pass
