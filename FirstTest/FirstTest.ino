#include "Motor.h"
#include "Constants.h"
#include "PID.h"
#include "Robot.h"


Robot Robot;
float vertical = 1;
float horizontal = 1;
float desiredDistance = 0;


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


}

void loop() {


  Robot.turnAroundItself(90);
  Robot.turnAroundItself(90);

  Robot.walkStraight(sqrt(sq(vertical) + sq(horizontal)));
  while (1) {
    Robot.desiredSpeedLeft = 0;
    Robot.desiredSpeedRight = 0;

    Robot.controlMotors();
  }


}
