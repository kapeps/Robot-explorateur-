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


#extint = pyb.ExtInt(Right_Motor._encoder_pin_A, pyb.ExtInt.IRQ_RISING, pyb.Pin.PULL_UP, callback)


def timerCallback(t):
  global romp
  romp.cruise(10, 10)
  

  
time = pyb.Timer(5, freq = 1, callback = timerCallback)



