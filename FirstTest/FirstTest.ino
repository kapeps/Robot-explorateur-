#include "Motor.h"
#include "Constants.h"
#include "PID.h"


float rightSpeed = 0;
float leftSpeed = 0;
int lastRightDistance = 0;
int lastLeftDistance = 0;


Motor Right_Motor(RIGHT_MOTOR_DIRECTION, ENCODER_RIGHT_A, ENCODER_RIGHT_B);
Motor Left_Motor(LEFT_MOTOR_DIRECTION, ENCODER_LEFT_A, ENCODER_LEFT_B);

void motor1ISR() {
  Right_Motor.readEncoder();
}
void motor2ISR() {
  Left_Motor.readEncoder();
}

PID control_left;
PID control_right;

int beginTime = 0;
float desiredAngle = 360;
float linearSpeed = 0.2;
float desiredSpeedLeft = 0.2;
float desiredSpeedRight = 0.2;
float vertical = 1;
float horizontal = 1;


void setup() {
  // put your setup code here, to run once:
  pinMode(RIGHT_MOTOR_PWM, OUTPUT);
  pinMode(LEFT_MOTOR_PWM, OUTPUT);
  attachInterrupt(digitalPinToInterrupt(Right_Motor.get_encoder_interrupt_pin()), motor1ISR, RISING);
  attachInterrupt(digitalPinToInterrupt(Left_Motor.get_encoder_interrupt_pin()), motor2ISR, RISING);
  Serial.begin(9600);



  control_left.setTunings(KP_LEFT, KI_LEFT, KD_LEFT);
  control_left.setSampleTime(1);
  control_left.setOutputLimits(-255, 255);

  control_right.setTunings(KP_RIGHT, KI_RIGHT, KD_RIGHT);
  control_right.setSampleTime(1);
  control_right.setOutputLimits(-255, 255);


}

void loop() {

  lastLeftDistance = Left_Motor.get_distance();
  lastRightDistance = Right_Motor.get_distance();

  while ((-Right_Motor.get_distance()+lastRightDistance + Left_Motor.get_distance() - lastLeftDistance) / 2 < desiredAngle * DISTANCE_BETWEEN_WHEELS * QUANTITY_OF_TICS / (2 * WHEEL_RADIUS * 360)) {
    desiredSpeedLeft = linearSpeed;
    desiredSpeedRight = -linearSpeed;
    controlMotors();
    Serial.println(rightSpeed);
  }
  //Stop
  beginTime = millis();
  while (millis() - beginTime < 200) {
    desiredSpeedLeft = 0;
    desiredSpeedRight = 0;
    controlMotors();
    Serial.println(rightSpeed);
  }

  
  lastLeftDistance = Left_Motor.get_distance();
  lastRightDistance = Right_Motor.get_distance();
  while (((+Right_Motor.get_distance()-lastRightDistance + Left_Motor.get_distance() - lastLeftDistance) / 2) < sqrt(sq(vertical)+sq(horizontal)) * 1000 * QUANTITY_OF_TICS /( 2 * WHEEL_RADIUS * 3.14))   {
    desiredSpeedLeft = linearSpeed;
    desiredSpeedRight = linearSpeed;
    controlMotors();
    Serial.println(rightSpeed);
  }



  while (1) {
    desiredSpeedLeft = 0;
    desiredSpeedRight = 0;

    controlMotors();
  }


}

void controlMotors() {
  rightSpeed = Right_Motor.calculate_speed();
  leftSpeed = Left_Motor.calculate_speed();
  control_right.setSetPoint(desiredSpeedRight);
  control_left.setSetPoint(desiredSpeedLeft);

  float outputLeft = control_left.compute(leftSpeed);
  float outputRight = control_right.compute(rightSpeed);

  if (desiredSpeedLeft == 0) {
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
