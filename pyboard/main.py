# main.py -- put your code here!
from pyb import *
import motor
import myconstants
distance_right = 0

Right_Motor = motor.Motor(myconstants.ENCODER_RIGHT_A, myconstants.ENCODER_RIGHT_B)

def callback(line):
  global distance_right
  distance_right += Right_Motor.readEcoder()


extint = pyb.ExtInt(Right_Motor._encoder_pin_A, pyb.ExtInt.IRQ_RISING, pyb.Pin.PULL_UP, callback)

while True :
  Right_Motor._distance = distance_right
  print(Right_Motor.get_distance())
  pyb.delay(100)


