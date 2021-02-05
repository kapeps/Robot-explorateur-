#include "robot.h"
#include "Motor.h"


Robot::Robot() {
  _control_left.setTunings(KP_LEFT, KI_LEFT, KD_LEFT);
  _control_left.setSampleTime(1);
  _control_left.setOutputLimits(-255, 255);

  _control_right.setTunings(KP_RIGHT, KI_RIGHT, KD_RIGHT);
  _control_right.setSampleTime(1);
  _control_right.setOutputLimits(-255, 255);

  /*
  _control_distance_left.setTunings(KP_LEFT_DISTANCE, KI_LEFT_DISTANCE, KD_LEFT_DISTANCE);
  _control_distance_left.setSampleTime(1);
  _control_distance_left.setOutputLimits(-LIMIT_VELOCITY, LIMIT_VELOCITY);

  _control_distance_right.setTunings(KP_RIGHT_DISTANCE, KI_RIGHT_DISTANCE, KD_RIGHT_DISTANCE);
  _control_distance_right.setSampleTime(1);
  _control_distance_right.setOutputLimits(-LIMIT_VELOCITY, LIMIT_VELOCITY);
  */
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
    desiredDistanceRight = -angle * DISTANCE_BETWEEN_WHEELS * QUANTITY_OF_TICS / (2 * WHEEL_RADIUS * 360);
    desiredDistanceLeft = angle * DISTANCE_BETWEEN_WHEELS * QUANTITY_OF_TICS / (2 * WHEEL_RADIUS * 360);

    while ((-Right_Motor.get_distance() + _lastRightDistance + Left_Motor.get_distance() - _lastLeftDistance) / 2 < angle * DISTANCE_BETWEEN_WHEELS * QUANTITY_OF_TICS / (2 * WHEEL_RADIUS * 360)) {

      controlMotors();
    }
  } else {
    desiredDistanceRight = angle * DISTANCE_BETWEEN_WHEELS * QUANTITY_OF_TICS / (2 * WHEEL_RADIUS * 360);
    desiredDistanceLeft = -angle * DISTANCE_BETWEEN_WHEELS * QUANTITY_OF_TICS / (2 * WHEEL_RADIUS * 360);
    while ((-Right_Motor.get_distance() + _lastRightDistance + Left_Motor.get_distance() - _lastLeftDistance) / 2 > angle * DISTANCE_BETWEEN_WHEELS * QUANTITY_OF_TICS / (2 * WHEEL_RADIUS * 360)) {


      controlMotors();
    }
  }

  //Stop
  _lastLeftDistance = Left_Motor.get_distance();
  _lastRightDistance = Right_Motor.get_distance();
  _beginTime = millis();
  while (millis() - _beginTime < 200) {
    desiredDistanceRight = 0;
    desiredDistanceLeft = 0;
    controlMotors();
  }
}

void Robot::walkStraight(float distanceMeters) {
  _lastLeftDistance = Left_Motor.get_distance();
  _lastRightDistance = Right_Motor.get_distance();

  if (distanceMeters > 0) {
    while (((+Right_Motor.get_distance() - _lastRightDistance + Left_Motor.get_distance() - _lastLeftDistance) / 2) < distanceMeters * 1000 * QUANTITY_OF_TICS / ( 2 * WHEEL_RADIUS * 3.14))   {
      desiredDistanceRight = distanceMeters * 1000 * QUANTITY_OF_TICS / ( 2 * WHEEL_RADIUS * 3.14);
      desiredDistanceLeft = distanceMeters * 1000 * QUANTITY_OF_TICS / ( 2 * WHEEL_RADIUS * 3.14);
      controlMotors();
    }
  } else {
    while (((+Right_Motor.get_distance() - _lastRightDistance + Left_Motor.get_distance() - _lastLeftDistance) / 2) > distanceMeters * 1000 * QUANTITY_OF_TICS / ( 2 * WHEEL_RADIUS * 3.14))   {
      desiredDistanceRight = -distanceMeters * 1000 * QUANTITY_OF_TICS / ( 2 * WHEEL_RADIUS * 3.14);
      desiredDistanceLeft = -distanceMeters * 1000 * QUANTITY_OF_TICS / ( 2 * WHEEL_RADIUS * 3.14);
      controlMotors();
    }
  }

  _lastLeftDistance = Left_Motor.get_distance();
  _lastRightDistance = Right_Motor.get_distance();
  _beginTime = millis();
  while (millis() - _beginTime < 200) {
    desiredDistanceRight = 0;
    desiredDistanceLeft = 0;
    controlMotors();
  }

}



void Robot::controlMotors() {
  /*_LeftDistance = Left_Motor.get_distance();
  _RightDistance = Right_Motor.get_distance();
  _control_distance_right.setSetPoint(desiredDistanceRight);
  _control_distance_left.setSetPoint(desiredDistanceLeft);



  desiredSpeedLeft = _control_distance_left.compute(_LeftDistance - _lastLeftDistance);
  desiredSpeedRight = _control_distance_right.compute(_RightDistance - _lastRightDistance);
  Serial.print("Desired Distance: "  );
  Serial.println(desiredDistanceLeft);

  Serial.print("DISTANCE: "  );
  Serial.println( _LeftDistance - _lastLeftDistance);
  Serial.print("Desired speed left: ");
  Serial.println(desiredSpeedLeft);
*/

  
  desiredSpeedRight = 0.1;
  desiredSpeedLeft = 0.1;


  _rightSpeed = Right_Motor.calculate_speed();
  _leftSpeed = Left_Motor.calculate_speed();
  _control_right.setSetPoint(desiredSpeedRight);
  _control_left.setSetPoint(desiredSpeedLeft);


  if (desiredDistanceLeft == 0 and (desiredSpeedLeft < 0.01)) {
    desiredSpeedLeft = 0;
  }
  if (desiredDistanceRight == 0 and (desiredSpeedRight < 0.01)) {
    desiredSpeedRight = 0;
  }


  float outputLeft = _control_left.compute(_leftSpeed);
  float outputRight = _control_right.compute(_rightSpeed);

  Serial.print("Desired pwm left: ");
  Serial.println(outputLeft);

  if (desiredSpeedLeft == 0 and (outputLeft < 10)) {
    outputLeft = 0;
  }
  if (desiredSpeedRight == 0 and (outputRight < 10)) {
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
