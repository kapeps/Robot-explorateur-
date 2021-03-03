#include "Motor.h"
#include "Constants.h"
#include "PID.h"
#include "Robot.h"
#include <math.h>
#include <Wire.h>



float vertical = 1;
float horizontal = 1;
float finalAngleToStart = -90;
float maximum_velocity = 0.4;
Robot Robot(maximum_velocity);



void motor1ISR() {
  Robot.Right_Motor.readEncoder();
}
void motor2ISR() {
  Robot.Left_Motor.readEncoder();
}




void setup() {
  Wire.begin(4);                // join i2c bus with address #4
  Wire.onReceive(receiveEvent); // register event

  pinMode(RIGHT_MOTOR_PWM, OUTPUT);
  pinMode(LEFT_MOTOR_PWM, OUTPUT);
  attachInterrupt(digitalPinToInterrupt(ENCODER_RIGHT_A), motor1ISR, RISING);
  attachInterrupt(digitalPinToInterrupt(ENCODER_LEFT_A), motor2ISR, RISING);
  Serial.begin(9600);


}

void loop() {



  /*Robot.robotMode = false;
    Robot.turnAroundItself(atan (horizontal / vertical) * 360 / (2 * PI));

    Robot.walkStraight(sqrt(sq(horizontal) + sq(vertical)));

    Robot.turnAroundItself(finalAngleToStart - atan (horizontal / vertical) * 360 / (2 * PI));


    while (1) {
    Robot.robotMode = true;
    Robot.desiredSpeedLeft = 0;
    Robot.desiredSpeedRight = 0;
    Robot.controlMotors();

    }

  */
  delay(100);

}

void receiveEvent(int howMany)
{
  String message = "";
  while (0 < Wire.available()) // loop through all but the last
  {
    char c = Wire.read(); // receive byte as a character
    message = message + c;
  }
  Serial.println(message);
  Robot.decodeI2CMessage(message);
}
