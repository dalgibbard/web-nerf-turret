String inputString = "";
bool stringComplete = false;
String axis = "";

#include <Servo.h>
Servo servoX; //pin2
Servo servoY; //pin3
Servo servoM; //pin4
Servo servoF; //pin5

void setup() {
    Serial.begin(9600);
    servoX.attach(2);
    servoY.attach(3);
    servoM.attach(4);
    servoF.attach(5);
    servoX.write(90);
    servoY.write(90);
    servoM.write(0);
    servoF.write(0);
}

void loop() {
    if (stringComplete){
      Serial.print("Command Received: ");
      Serial.print(axis);
      Serial.println(inputString);
      if ( axis == "X" ){
        servoX.write(inputString.toInt());
        Serial.print("Setting X Axis to ");
        Serial.println(inputString);
      }
      if ( axis == "Y" ){
        servoY.write(inputString.toInt());
        Serial.print("Setting Y Axis to ");
        Serial.println(inputString);
      }
      if ( axis == "M" ){
        servoM.write(inputString.toInt());
        Serial.print("Setting Motors to ");
        Serial.println(inputString);
      }
      if ( axis == "F" ){
        servoF.write(inputString.toInt());
        Serial.print("Setting Firing Arm to ");
        Serial.println(inputString);
      }
      stringComplete = false;
      inputString = "";
      axis = "";
    }
}

void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read(); 
    if (inChar == '\n') {
      stringComplete = true;
    } else if (inChar == 'X'){
      axis = "X";
    } else if (inChar == 'Y'){
      axis = "Y";
    } else if (inChar == 'M'){
      axis = "M";
    } else if (inChar == 'F'){
      axis = "F";
    } else if (isDigit(inChar)){
         inputString += (char)inChar;
    } else {
       Serial.print("Invalid Value Received: ");
       Serial.println(inChar);
    }
  }
}
