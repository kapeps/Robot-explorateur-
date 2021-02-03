#include "Motor.h"
#include "Constants.h"
#include "PID.h"
long lastMillis = 0;
int lastCount = 0;
int initial_distance = 0;

float rightSpeed = 0;
float leftSpeed = 0;

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
float desiredSpeedLeft = 0.22;
float desiredSpeedRight = 0.22;

void setup() {
  // put your setup code here, to run once:
  pinMode(RIGHT_MOTOR_PWM, OUTPUT);
  pinMode(LEFT_MOTOR_PWM, OUTPUT);
  attachInterrupt(digitalPinToInterrupt(Right_Motor.get_encoder_interrupt_pin()), motor1ISR, RISING);
  attachInterrupt(digitalPinToInterrupt(Left_Motor.get_encoder_interrupt_pin()), motor2ISR, RISING);
  Serial.begin(9600);



  control_left.setSetPoint(desiredSpeedLeft);
  control_left.setTunings(KP_LEFT, KI_LEFT, KD_LEFT);
  control_left.setSampleTime(1);
  control_left.setOutputLimits(-255, 255);

  control_right.setSetPoint(desiredSpeedRight);
  control_right.setTunings(KP_RIGHT, KI_RIGHT, KD_RIGHT);
  control_right.setSampleTime(1);
  control_right.setOutputLimits(-255, 255);


  analogWrite(RIGHT_MOTOR_PWM, 100);
}

void loop() {

  //Serial.print("rightSpeed : ");
  //Serial.println(rightSpeed);
  //Serial.print("leftSpeed : ");
  //Serial.println(leftSpeed);
  controlMotors();
  Serial.println(Left_Motor.get_distance());


}

void controlMotors() {
  rightSpeed = Right_Motor.calculate_speed();
  leftSpeed = Left_Motor.calculate_speed();

  float outputLeft = control_left.compute(leftSpeed);
  float outputRight = control_right.compute(rightSpeed);
  //Serial.println(outputRight);

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
