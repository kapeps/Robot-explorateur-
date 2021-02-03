#ifndef MOTOR_H
#define MOTOR_H

#include <Arduino.h>
#include "Constants.h"

class Motor {
  public:
    Motor(byte pin, byte encoder_pin_A, byte encoder_pin_B);
    void readEncoder();
    byte get_encoder_interrupt_pin();
    int get_distance();
    float calculate_speed();

  private:

    byte _pin;
    byte _encoder_pin_A;
    byte _encoder_pin_B;
    volatile int _distance;
    int _lastDistance;
    long _lastMillis;
    float _speed;
};

#endif
