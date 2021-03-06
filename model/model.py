import json
import numpy as np
from time import sleep


class LaserModel(object):
    def __init__(self, servos, servoMin, servoMax, servoXCenter, servoYCenter, firingarm, motorspeed):
        self.xAxisValue = 0
        self.yAxisValue = 0
        self.servos = servos
        self.servoMin = servoMin
        self.servoMax = servoMax
        self.setaxisx(servoXCenter)
        self.setaxisy(servoYCenter)
        self.firingArm = firingarm
        self.motorspeed = motorspeed
        self.currentmotorspeed = 0
        self.targetCalibration = None
        self.servoCalibration = None
        self.transform = None
        self.calibrationFile = 'calibration.json'
        self._loadCalibration()
        self._generateTransform()

    def setaxisx(self, value):
        self.xAxisValue = self._validateAxis(value)
        self.servos.setaxisx(self.xAxisValue)

    def getaxisx(self):
        return self.xAxisValue

    def setaxisy(self, value):
        self.yAxisValue = self._validateAxis(value)
        self.servos.setaxisy(self.yAxisValue)

    def getaxisy(self):
        return self.yAxisValue

    def setCalibration(self, targetCalibration, servoCalibration):
        self.targetCalibration = targetCalibration
        self.servoCalibration = servoCalibration
        self._generateTransform()
        self._saveCalibration()

    def getCalibration(self):
        return self.targetCalibration, self.servoCalibration

    def fire(self):
        self.setFiringArm(0)
        self.armMotor(self.motorspeed)
        sleep(0.4)
        self.setFiringArm(self.firingArm)
        sleep(0.3)
        self.setFiringArm(0)
        sleep(0.5)
        self.armMotor(0)

    def target(self, x, y):
        """Transform screen coordinate position to servo coordinate position and move servos accordingly."""
        if self.transform == None:
            raise ValueError('Calibration not set!')
        screen = np.array([float(x), float(y), 1.0])
        servo = self.transform.dot(screen)
        servo = servo/servo[2]
        self.setaxisx(round(servo[0]))
        self.setaxisy(round(servo[1]))
#        if self.firingstate == True:
#            self.armMotor(self.motorspeed)
#            self.setFiringArm(0)
#            sleep(300)
#            self.setFiringArm(self.firingArm)
#            sleep(300)
#            self.setFiringArm(0)
#            sleep(300)
#            self.armMotor(0)

    def firingstate(self, state):
        if state == False:
            self.armMotor(0)
            self.firingstate = False
        if state == True:
            self.firingstate = True

    def armMotor(self, value):
        # If current motor speed is less than desired speed
        if self.currentmotorspeed < value:
            while not int(self.currentmotorspeed) == int(value):
                # If the different is greater than 20
                if (self.currentmotorspeed + 20 <= value):
                    self.currentmotorspeed = int(self.currentmotorspeed) + 20
                    self.servos.setMotor(self.currentmotorspeed)
                    sleep(0.1)
                else:
                    self.currentmotorspeed = value
                    self.servos.setMotor(self.currentmotorspeed)
        # If current motor speed is higher than desired speed
        elif self.currentmotorspeed > value:
            while not int(self.currentmotorspeed) == int(value):
                # If the difference is greater than 20
                if self.currentmotorspeed - 20 >= value:
                    self.currentmotorspeed -= 20
                    self.servos.setMotor(self.currentmotorspeed)
                    sleep(0.1)
                else:
                    self.currentmotorspeed = value
                    self.servos.setMotor(self.currentmotorspeed)
        else:
            self.currentmotorspeed = value
            self.servos.setMotor(value)

    def setFiringArm(self, value):
        self.servos.setFiring(value)

    def _validateAxis(self, value):
        """Validate servo value is within range of allowed values."""
        try:
            v = int(value)
            if v < self.servoMin or v > self.servoMax:
                raise ValueError()
            return v
        except:
            raise ValueError('Invalid value! Must be a value between %i and %i.' % (self.servoMin, self.servoMax))

    def _loadCalibration(self):
        """Load calibration data from disk."""
        try:
            with open(self.calibrationFile, 'r') as file:
                cal = json.loads(file.read())
                self.targetCalibration = cal['targetCalibration']
                self.servoCalibration = cal['servoCalibration']
        except IOError:
            pass

    def _saveCalibration(self):
        """Save calibration data to disk."""
        with open(self.calibrationFile, 'w') as file:
            file.write(json.dumps({'targetCalibration': self.targetCalibration, 'servoCalibration': self.servoCalibration }))

    def _generateTransform(self):
        """ 
        Generate the matrix to transform a quadrilaterl in target click coordinates to a quadrilateral in
        servo movement coordinates using a perspective transformation.  
        See http://alumni.media.mit.edu/~cwren/interpolator/ for more details.
        """
        if self.targetCalibration == None or self.servoCalibration == None:
            return
        # Define some variables to make the matrices easier to read
        x1 = float(self.targetCalibration[0]['x'])
        y1 = float(self.targetCalibration[0]['y'])
        x2 = float(self.targetCalibration[1]['x'])
        y2 = float(self.targetCalibration[1]['y'])
        x3 = float(self.targetCalibration[2]['x'])
        y3 = float(self.targetCalibration[2]['y'])
        x4 = float(self.targetCalibration[3]['x'])
        y4 = float(self.targetCalibration[3]['y'])
        X1 = float(self.servoCalibration[0]['x'])
        Y1 = float(self.servoCalibration[0]['y'])
        X2 = float(self.servoCalibration[1]['x'])
        Y2 = float(self.servoCalibration[1]['y'])
        X3 = float(self.servoCalibration[2]['x'])
        Y3 = float(self.servoCalibration[2]['y'])
        X4 = float(self.servoCalibration[3]['x'])
        Y4 = float(self.servoCalibration[3]['y'])
        # Define matrices
        A = np.array([  [x1, y1,  1,  0,  0,  0, -X1*x1, -X1*y1],
                        [ 0,  0,  0, x1, y1,  1, -Y1*x1, -Y1*y1],
                        [x2, y2,  1,  0,  0,  0, -X2*x2, -X2*y2],
                        [ 0,  0,  0, x2, y2,  1, -Y2*x2, -Y2*y2],
                        [x3, y3,  1,  0,  0,  0, -X3*x3, -X3*y3],
                        [ 0,  0,  0, x3, y3,  1, -Y3*x3, -Y3*y3],
                        [x4, y4,  1,  0,  0,  0, -X4*x4, -X4*y4],
                        [ 0,  0,  0, x4, y4,  1, -Y4*x4, -Y4*y4] ])
        B = np.array([X1, Y1, X2, Y2, X3, Y3, X4, Y4])
        # Solve for coefficients x in equation Ax = B
        x = np.linalg.solve(A, B)
        # Set transformation matrix with coefficients
        self.transform = np.array([  [x[0], x[1], x[2]],
                                     [x[3], x[4], x[5]],
                                     [x[6], x[7],  1.0] ])
