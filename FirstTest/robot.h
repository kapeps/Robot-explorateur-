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
    signed int desiredDistanceRight = 0;
    signed int desiredDistanceLeft = 0;

    float _linearSpeed = 0.5;
    int _lastRightDistance = 0;
    int _lastLeftDistance = 0;
    bool robotMode = false;//false for controling via motion, true for giving direct speed information

    
  private:
    PID _control_left;
    PID _control_right;

    PID _control_distance_left;
    PID _control_distance_right;
    
    float _rightSpeed = 0;
    float _leftSpeed = 0;

    int _RightDistance = 0;
    int _LeftDistance = 0;
    int _beginTime = 0;
    float _desiredAngle = 360;




};

#endif
