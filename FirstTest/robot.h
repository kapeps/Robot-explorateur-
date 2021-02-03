#ifndef ROBOT_H
#define ROBOT_H

#include <Arduino.h>
#include "Constants.h"
#include "Motor.h"
#include "PID.h"

class Robot {
  public:
    Robot();
    Motor Right_Motor = Motor(RIGHT_MOTOR_DIRECTION, ENCODER_RIGHT_A, ENCODER_RIGHT_B);
    Motor Left_Motor = Motor(LEFT_MOTOR_DIRECTION, ENCODER_LEFT_A, ENCODER_LEFT_B);
 
    
    void controlItEntirely(float angle);
    void turnAroundItself(float angle);
    void walkStraight(float distanceMeters);
    void controlMotors();

    
    float desiredSpeedLeft = 0.5;
    float desiredSpeedRight = 0.5;


    
  private:
    PID _control_left;
    PID _control_right;

    
    float _rightSpeed = 0;
    float _leftSpeed = 0;
    int _lastRightDistance = 0;
    int _lastLeftDistance = 0;
    int _beginTime = 0;
    float _desiredAngle = 360;
    float _linearSpeed = 0.5;




};

#endif
