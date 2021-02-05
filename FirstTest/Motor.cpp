#include "Motor.h"


Motor::Motor(byte pin, byte encoder_pin_A, byte encoder_pin_B) {
  _pin = pin;
  _encoder_pin_A = encoder_pin_A;
  _encoder_pin_B = encoder_pin_B;
}

void Motor::readEncoder() {
  if (digitalRead(this->_encoder_pin_B)) {
    _distance++;
  }
  else {
    _distance--;
  }
}

byte Motor::get_encoder_interrupt_pin() {
  return _encoder_pin_A;
}

float Motor::calculate_speed() {
  long deltaTime = millis() - _lastMillis;
  if(deltaTime > 2){
    _lastMillis = millis();
    _speed = (_distance - _lastDistance) * 2 * 3.14 * WHEEL_RADIUS / deltaTime / QUANTITY_OF_TICS;
    _lastDistance = _distance;
  }
  return _speed;
}

int Motor::get_distance() {
  return _distance;
}
