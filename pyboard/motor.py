import myconstants
import machine
import pyb
import time

class Motor:
    
    def __init__(self, encoder_pin_A_number, encoder_pin_B_number):
        self._encoder_pin_A = machine.Pin("X"+str(encoder_pin_A_number), machine.Pin.IN, machine.Pin.PULL_UP)
        self._encoder_pin_B = machine.Pin("X"+str(encoder_pin_B_number), machine.Pin.IN, machine.Pin.PULL_UP)
        self._distance = 0 
        self._lastDistance = 0
        self._lastMillis = 0
        self._speed = 0

    def readEncoder(self):
        if(self._encoder_pin_B.value() == 1):
            self._distance+=1
        else:
            self._distance-=1
        

    def calculate_speed(self):
        deltaTime = time.ticks_ms() - self._lastMillis
        if(deltaTime > 2):
            self._lastMillis = time.ticks_ms()
            self._speed = (self._distance - self._lastDistance) * 2 * 3.14 * WHEEL_RADIUS / deltaTime / QUANTITY_OF_TICS
            self._lastDistance = self._distance
        return self._speed

    def get_distance(self):
        return self._distance    