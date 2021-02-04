#include "robot.h"
#include "Motor.h"


Robot::Robot() {
  _control_left.setTunings(KP_LEFT, KI_LEFT, KD_LEFT);
  _control_left.setSampleTime(1);
  _control_left.setOutputLimits(-255, 255);

  _control_right.setTunings(KP_RIGHT, KI_RIGHT, KD_RIGHT);
  _control_right.setSampleTime(1);
  _control_right.setOutputLimits(-255, 255);

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
  if ( angle > 0) {
    while ((-Right_Motor.get_distance() + _lastRightDistance + Left_Motor.get_distance() - _lastLeftDistance) / 2 < angle * DISTANCE_BETWEEN_WHEELS * QUANTITY_OF_TICS / (2 * WHEEL_RADIUS * 360)) {
      desiredSpeedLeft = _linearSpeed;
      desiredSpeedRight = -_linearSpeed;
      controlMotors();
    }
  } else {
    while ((-Right_Motor.get_distance() + _lastRightDistance + Left_Motor.get_distance() - _lastLeftDistance) / 2 > angle * DISTANCE_BETWEEN_WHEELS * QUANTITY_OF_TICS / (2 * WHEEL_RADIUS * 360)) {
      desiredSpeedLeft = -_linearSpeed;
      desiredSpeedRight = _linearSpeed;
      controlMotors();
    }
  }

  //Stop
  _beginTime = millis();
  while (millis() - _beginTime < 200) {
    desiredSpeedLeft = 0;
    desiredSpeedRight = 0;
    controlMotors();
  }
}

void Robot::walkStraight(float distanceMeters) {
  _lastLeftDistance = Left_Motor.get_distance();
  _lastRightDistance = Right_Motor.get_distance();

  if (distanceMeters > 0) {
    while (((+Right_Motor.get_distance() - _lastRightDistance + Left_Motor.get_distance() - _lastLeftDistance) / 2) < distanceMeters * 1000 * QUANTITY_OF_TICS / ( 2 * WHEEL_RADIUS * 3.14))   {
      desiredSpeedLeft = _linearSpeed;
      desiredSpeedRight = _linearSpeed;
      controlMotors();
    }
  } else {
    while (((+Right_Motor.get_distance() - _lastRightDistance + Left_Motor.get_distance() - _lastLeftDistance) / 2) > distanceMeters * 1000 * QUANTITY_OF_TICS / ( 2 * WHEEL_RADIUS * 3.14))   {
      desiredSpeedLeft = -_linearSpeed;
      desiredSpeedRight = -_linearSpeed;
      controlMotors();
    }
  }

  _beginTime = millis();
  while (millis() - _beginTime < 200) {
    desiredSpeedLeft = 0;
    desiredSpeedRight = 0;
    controlMotors();
  }

}


void Robot::controlMotors() {
  _rightSpeed = Right_Motor.calculate_speed();
  _leftSpeed = Left_Motor.calculate_speed();
  _control_right.setSetPoint(desiredSpeedRight);
  _control_left.setSetPoint(desiredSpeedLeft);

  float outputLeft = _control_left.compute(_leftSpeed);
  float outputRight = _control_right.compute(_rightSpeed);

  if (desiredSpeedLeft == 0 ) {
    outputLeft = 0;
  }
  if (desiredSpeedRight == 0) {
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
