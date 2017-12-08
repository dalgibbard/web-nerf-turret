from flask import *
import json, sys

import model
import servos

# Flask app configuration
DEBUG = True

SERVO_MIN = 0 # Minimum rotation value for the servo, should be -90 degrees of rotation.
SERVO_MAX = 180 # Maximum rotation value for the servo, should be 90 degrees of rotation.
SERVO_XCENTER = 130
SERVO_YCENTER = 85
MOTOR_VALUE = 105 # Speed setting for motor
FIRING_VALUE = 120 # Servo throw for firing arm
FIRING = False
BAUD_RATE = 9600
SERIAL_PORT = "/dev/ttyS0"

# Initialize flask app
app = Flask(__name__)
app.config.from_object(__name__)

# Setup the real servo when running on a Raspberry Pi
servos = servos.Servos(BAUD_RATE, SERIAL_PORT)

model = model.LaserModel(servos, SERVO_MIN, SERVO_MAX, SERVO_XCENTER, SERVO_YCENTER, FIRING_VALUE, MOTOR_VALUE)

# Main view for rendering the web page
@app.route('/')
def main():
    return render_template('main.html', model=model)

# Error handler for API call failures
@app.errorhandler(ValueError)
def valueErrorHandler(error):
    return jsonify({'result': error.message}), 500

def successNoResponse():
    return jsonify({'result': 'success'}), 204

# API calls used by the web app
@app.route('/set/servo/xaxis/<xaxis>', methods=['PUT'])
def setServoXAxis(xaxis):
    model.setXAxis(xaxis)
    return successNoResponse()

@app.route('/set/servo/yaxis/<yaxis>', methods=['PUT'])
def setServoYAaxis(yaxis):
    model.setYAxis(yaxis)
    return successNoResponse()

@app.route('/set/servos/<xaxis>/<yaxis>', methods=['PUT'])
def setServos(xaxis, yaxis):
    model.setXAxis(xaxis)
    model.setYAxis(yaxis)
    return successNoResponse()

@app.route('/get/servos', methods=['GET'])
def getServos():
    return jsonify({'xaxis': model.getXAxis(), 'yaxis': model.getYAxis() }), 200

@app.route('/get/calibration', methods=['GET'])
def getCalibration():
    return jsonify({'target': model.targetCalibration, 'servo': model.servoCalibration}), 200

@app.route('/set/calibration', methods=['POST'])
def setCalibration():
    model.setCalibration(json.loads(request.form['targetCalibration']), json.loads(request.form['servoCalibration']))
    return successNoResponse()

@app.route('/target/<int:x>/<int:y>', methods=['PUT'])
def target(x, y):
    model.target(x, y)
    return successNoResponse()

@app.route('/fire', methods=['GET'])
def fire(state):
    model.fire()
    return successNoResponse()

# Start running the flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0')
