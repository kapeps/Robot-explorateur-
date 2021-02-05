#include "Motor.h"
#include "Constants.h"
#include "PID.h"
#include "Robot.h"
#include <math.h>

Robot Robot;
float vertical = 1;
float horizontal = 1;
float finalAngleToStart = 0;

void motor1ISR() {
  Robot.Right_Motor.readEncoder();
}
void motor2ISR() {
  Robot.Left_Motor.readEncoder();
}




void setup() {
  // put your setup code here, to run once:
  pinMode(RIGHT_MOTOR_PWM, OUTPUT);
  pinMode(LEFT_MOTOR_PWM, OUTPUT);
  attachInterrupt(digitalPinToInterrupt(ENCODER_RIGHT_A), motor1ISR, RISING);
  attachInterrupt(digitalPinToInterrupt(ENCODER_LEFT_A), motor2ISR, RISING);
  Serial.begin(9600);
  Robot._linearSpeed = 0.4;

}

void loop() {

  Robot.turnAroundItself(atan (horizontal / vertical) * 360 / (2 * PI));
 
  Robot._lastLeftDistance = 0;
  Robot._lastRightDistance = 0;
  while (1) {
    Robot.desiredDistanceRight = 0;
    Robot.desiredDistanceLeft = 0;
    Robot.controlMotors();
  }


}
