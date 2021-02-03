#ifndef ENCODERS_H
#define ENCODERS_H


volatile long distance_right = 0;
volatile long distance_left = 0;

//attach interrupts on rising ENCODER_RIGHT_1 ENCODER_LEFT_1

void readEncoderRight() {
  if (digitalRead(ENCODER_RIGHT_B)){
    distance_right++;
  }
  else{
    distance_right--;
  }
}

void readEncoderLeft() {
  if (digitalRead(ENCODER_LEFT_A)){
    distance_left--;
  }
  else{
    distance_left++;
  }
}

void startInts() {
  attachInterrupt(digitalPinToInterrupt(ENCODER_RIGHT_A), readEncoderRight, RISING);
  attachInterrupt(digitalPinToInterrupt(ENCODER_LEFT_B), readEncoderLeft, RISING);
}

void resetDistances() {
  distance_left = 0;
  distance_right = 0;
}

#endif
