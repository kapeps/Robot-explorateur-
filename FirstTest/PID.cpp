#include "PID.h"
#include <Arduino.h>

PID::PID()
{

}

void PID::setOutputLimits(float minOutput, float maxOutput)
{
  _minOutput = minOutput;
  _maxOutput = maxOutput;

  _lastOutput = constrain(_lastOutput, _minOutput, _maxOutput);
  _integrativeSum = constrain(_integrativeSum, _minOutput, _maxOutput);
}

void PID::setTunings(float kP, float kI, float kD)
{
  _kP = kP;
  _kI = kI;
  _kD = kD;
}


void PID::setTunings(float *parameters)
{
  _kP = parameters[0];
  _kI = parameters[1];
  _kD = parameters[2];
}
  
void PID::setSampleTime(unsigned long newSampleTime)
{
  if (newSampleTime > 0)
  {
    _sampleTime = newSampleTime;
  }
}

void PID::setSetPoint(float setPoint)
{
  _setPoint = setPoint;
}

float PID::compute(float input)
{
  unsigned long now = millis();
  unsigned long timeChange = (now - _lastRunTime);
  if (timeChange < _sampleTime)
  {
    return _lastOutput;
  }

  float error = _setPoint - input;

  _integrativeSum += error * _kI * _sampleTime;
  
  _integrativeSum = constrain(_integrativeSum, _minOutput, _maxOutput);


  float dInput = (_kD * (input - _lastInput)) / _sampleTime;
  float dError = -dInput;
  float alfa = 1;
  dError = dError*alfa + _lastDerivative*(1-alfa);
  _lastDerivative = dError;

  _lastOutput = (_kP * error) + (_integrativeSum) + (dError);

  _lastOutput = constrain(_lastOutput, _minOutput, _maxOutput);

  _lastInput = input;
  _lastRunTime = now;
  return _lastOutput;
}
