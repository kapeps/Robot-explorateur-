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
while not switch.value():
    try:
        data = i2c.recv(5)
    except OSError:
        data = None

    if data is None:
        print("None")
    else:
        romp.decodeI2CMessage(data)

    pyb.delay(1500)





