import myconstants
import machine
import pyb
import time

class Motor:
    _encoder_pin_A = machine.Pin("X"+str(1), machine.Pin.IN, machine.Pin.PULL_UP)
    _encoder_pin_B = machine.Pin("X"+str(1), machine.Pin.IN, machine.Pin.PULL_UP)
    _distance = 0 
    _lastDistance = 0
    _lastMillis = 0
    _speed = 0


    def __init__(self, encoder_pin_A_number, encoder_pin_B_number):
        self._encoder_pin_A = machine.Pin("X"+str(encoder_pin_A_number), machine.Pin.IN, machine.Pin.PULL_UP)
        self._encoder_pin_B = machine.Pin("X"+str(encoder_pin_B_number), machine.Pin.IN, machine.Pin.PULL_UP)
        _distance = 0 
        _lastDistance = 0
        _lastMillis = 0
        _speed = 0

    def readEcoder(self):
        if(self._encoder_pin_B.value() == 1):
            return 1
        else:
            return -1
        

    def calculate_speed(self):
        deltaTime = time.ticks_ms() - self._lastMillis
        if(deltaTime > 2):
            self._lastMillis = time.ticks_ms()
            self._speed = (self._distance - self._lastDistance) * 2 * 3.14 * myconstants.WHEEL_RADIUS / deltaTime / myconstants.QUANTITY_OF_TICS
            self._lastDistance = self._distance
        return self._speed

    def get_distance(self):
        return self._distance    