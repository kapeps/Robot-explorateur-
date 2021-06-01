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


i2c = pyb.I2C(2)
i2c.init(pyb.I2C.SLAVE, addr = 0x04)
switch = pyb.Switch()

data = bytearray(5)
check = bytearray(1)

while not switch.value():
    try:
        data = i2c.recv(1, timeout=50)
        if data[0] == 45:
            data = i2c.recv(5, timeout=200)
            romp.decodeI2CMessage(data)
    except OSError:
        data = None


    #pyb.delay(1500)





def timerCallback(t):
  global romp
  romp.cruise(-10, -10) 

  
#time = pyb.Timer(5, freq = 1, callback = timerCallback)



