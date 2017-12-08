import serial

class Servos(object):
    def __init__(self, baudrate, serialport):
        self.baudrate = baudrate
        self.serialport = serialport

    def writeSerial(self, command):
        try:
            ser = serial.Serial(self.serialport, self.baudrate, timeout=1)
            ser.close()
            ser.open()
            ser.write(str(command)+"\n")
        except serial.Exception:
            continue

    def setXAxis(self, value):
        self.writeSerial("X"+str(value))

    def setYAxis(self, value):
        self.writeSerial("Y"+str(value))

    def setMotor(self, value):
        self.writeSerial("M"+str(value))

    def setFiring(self, value):
        self.writeSerial("F"+str(value))