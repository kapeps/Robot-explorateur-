import pyb
from pyb import Pin, Timer, ExtInt

import micropython


class PID:
    def __init__(self):
        self._minOutput = 0
        self._maxOutput = 0
        self._kP = 0
        self._kI = 0
        self._kD = 0
        self._sampleTime = 0
        self._setPoint = 0
        self._integrativeSum = 0
        self._lastOutput = 0
        self._lastInput = 0
        self._lastDerivative = 0
        self._lastRunTime = 0

    def constrain(self,value, minValue,maxValue):
        if (value>maxValue):
            return maxValue
        elif (value<minValue):
            return minValue
        else:
            return value

    def setOutputLimits(self,minOutput, maxOutput):
        self._minOutput = minOutput;
        self._maxOutput = maxOutput;
        self._lastOutput = self.constrain(self._lastOutput, self._minOutput, self._maxOutput);
        self._integrativeSum = self.constrain(self._integrativeSum, self._minOutput, self._maxOutput);

    def setTunings(self,kP, kI, kD):
        self._kP = kP
        self._kI = kI
        self._kD = kD
    
    def setSampleTime(self,newSampleTime):
        if (newSampleTime > 0):
            self._sampleTime = newSampleTime
        
    def setSetPoint(self,setPoint):
        self._setPoint = setPoint

    def compute(self,input):
        now = pyb.millis()
        timeChange = (now - self._lastRunTime)
        if (timeChange < self._sampleTime):
            return self._lastOutput
        
        error = self._setPoint - input
        self._integrativeSum += error * self._kI * self._sampleTime
        self._integrativeSum = self.constrain(self._integrativeSum, self._minOutput, self._maxOutput)
        
        dInput = (self._kD * (input - self._lastInput)) 
        dError = -dInput
        
        self._lastOutput = (self._kP * error) + (self._integrativeSum) + (dError)
        self._lastOutput = self.constrain(self._lastOutput, self._minOutput, self._maxOutput)

        self._lastInput = input
        self._lastRunTime = now
        self._lastDerivative = dError

        return self._lastOutput
