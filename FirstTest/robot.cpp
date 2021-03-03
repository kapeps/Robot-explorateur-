#include "robot.h"
#include "Motor.h"


Robot::Robot(float maximumVelocity) {
  _maximumVelocity = maximumVelocity;
  _control_left.setTunings(KP_LEFT, KI_LEFT, KD_LEFT);
  _control_left.setSampleTime(1);
  _control_left.setOutputLimits(-255, 255);

  _control_right.setTunings(KP_RIGHT, KI_RIGHT, KD_RIGHT);
  _control_right.setSampleTime(1);
  _control_right.setOutputLimits(-255, 255);


  _control_distance_left.setTunings(KP_LEFT_DISTANCE, KI_LEFT_DISTANCE, KD_LEFT_DISTANCE);
  _control_distance_left.setSampleTime(1);
  _control_distance_left.setOutputLimits(-_maximumVelocity, _maximumVelocity);

  _control_distance_right.setTunings(KP_RIGHT_DISTANCE, KI_RIGHT_DISTANCE, KD_RIGHT_DISTANCE);
  _control_distance_right.setSampleTime(1);
  _control_distance_right.setOutputLimits(-_maximumVelocity, _maximumVelocity);
}



void Robot::controlItEntirely(float angle) {
  bool controlIt = 1;
  while (controlIt) {
    //receive controllIt, and desired speeds
    controlMotors();
  }

  _beginTime = millis();
  while (millis() - _beginTime < 200) {
    desiredSpeedLeft = 0;
    desiredSpeedRight = 0;
    controlMotors();
  }
}
void Robot::turnAroundItself(float angle) {

  _lastLeftDistance = Left_Motor.get_distance();
  _lastRightDistance = Right_Motor.get_distance();
  _LeftDistance = _lastLeftDistance;
  _RightDistance = _lastRightDistance;
  desiredDistanceRight = -angle * DISTANCE_BETWEEN_WHEELS * QUANTITY_OF_TICS / (2 * WHEEL_RADIUS * 360);
  desiredDistanceLeft = angle * DISTANCE_BETWEEN_WHEELS * QUANTITY_OF_TICS / (2 * WHEEL_RADIUS * 360);

  while ((desiredDistanceLeft - _LeftDistance + _lastLeftDistance) > 2 or (desiredDistanceRight - _RightDistance + _lastRightDistance) > 2) {

    controlMotors();

  }

  //Stop
  _beginTime = millis();
  while (millis() - _beginTime < 50) {
    desiredDistanceRight = _RightDistance - _lastRightDistance;
    desiredDistanceLeft = _LeftDistance - _lastLeftDistance;
    controlMotors();
  }
}

void Robot::walkStraight(float distanceMeters) {
  _lastLeftDistance = Left_Motor.get_distance();
  _lastRightDistance = Right_Motor.get_distance();
  _LeftDistance = _lastLeftDistance;
  _RightDistance = _lastRightDistance;
  desiredDistanceRight = distanceMeters * 1000 * QUANTITY_OF_TICS / ( 2 * WHEEL_RADIUS * 3.14);
  desiredDistanceLeft = distanceMeters * 1000 * QUANTITY_OF_TICS / ( 2 * WHEEL_RADIUS * 3.14);

  while ((desiredDistanceLeft - _LeftDistance + _lastLeftDistance) > 2 or (desiredDistanceRight - _RightDistance + _lastRightDistance) > 2) {

    controlMotors();

  }


  _beginTime = millis();
  while (millis() - _beginTime < 50) {
    desiredDistanceRight = _RightDistance - _lastRightDistance;
    desiredDistanceLeft = _LeftDistance - _lastLeftDistance;
    controlMotors();
  }

}


void Robot::controlMotors() {

  if (robotMode == false) {
    _LeftDistance = Left_Motor.get_distance();
    _RightDistance = Right_Motor.get_distance();
    _control_distance_right.setSetPoint(desiredDistanceRight);
    _control_distance_left.setSetPoint(desiredDistanceLeft);

    desiredSpeedRight = _control_distance_right.compute(_RightDistance - _lastRightDistance);
    desiredSpeedLeft = _control_distance_left.compute(_LeftDistance - _lastLeftDistance);

  }




  _rightSpeed = Right_Motor.calculate_speed();
  _leftSpeed = Left_Motor.calculate_speed();
  _control_right.setSetPoint(desiredSpeedRight);
  _control_left.setSetPoint(desiredSpeedLeft);

  float outputLeft = _control_left.compute(_leftSpeed);
  float outputRight = _control_right.compute(_rightSpeed);

  if (abs(desiredSpeedLeft) < 0.02  and (abs(outputLeft) < 10)) {
    outputLeft = 0;
  }
  if (abs(desiredSpeedRight) < 0.02 and (abs(outputRight) < 10)) {
    outputRight = 0;
  }

  if (outputLeft > 0) {
    analogWrite(LEFT_MOTOR_PWM, outputLeft );
    digitalWrite(LEFT_MOTOR_DIRECTION, LOW);
  }
  else {
    analogWrite(LEFT_MOTOR_PWM, -outputLeft  );
    digitalWrite(LEFT_MOTOR_DIRECTION, HIGH);

  }


  if (outputRight > 0) {
    analogWrite(RIGHT_MOTOR_PWM, 1 * outputRight );
    digitalWrite(RIGHT_MOTOR_DIRECTION, LOW);
  }
  else {
    analogWrite(RIGHT_MOTOR_PWM, -1 * outputRight);
    digitalWrite(RIGHT_MOTOR_DIRECTION, HIGH);

  }

}


void Robot::decodeI2CMessage(String message) {
  if (message[0] == '0') {
    Serial.println("Mode 0");
    robotMode = true;
    desiredSpeedLeft = (int)message[1]+256*(int)message[2];
    desiredSpeedRight = (int)message[3]+256*(int)message[4];
    controlMotors();
  } else if (message[0] == '1') {
    Serial.println("Mode 1");

  } else if (message[0] == '2') {
    Serial.println("Mode 2");

    
  }else{
    Serial.println(message[0]);
  }

}
