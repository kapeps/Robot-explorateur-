# main.py -- put your code here!
import pyb
import motor
import myconstants
from romipyb import RomiPlatform
from PID import PID

#Right_Motor = motor.Motor(myconstants.ENCODER_RIGHT_A, myconstants.ENCODER_RIGHT_B)
romp = RomiPlatform()
lm = romp.leftmotor
rm = romp.rightmotor
romp.move(1, 1)



#extint = pyb.ExtInt(Right_Motor._encoder_pin_A, pyb.ExtInt.IRQ_RISING, pyb.Pin.PULL_UP, callback)


def timerCallback(t):
  global romp
  romp.move(1, 1)
  print("move")

  
time = pyb.Timer(4, freq = 1, callback = timerCallback)



