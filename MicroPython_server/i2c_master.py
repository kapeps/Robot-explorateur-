from machine import Pin
from machine import I2C #pas de timeout pour le I2C hardware
from machine import SoftI2C #pas de timeout pour le I2C hardware
from uarray import array
import ucollections as collections

import uasyncio

import time



COMMAND_LIDAR_GET_SCAN = b'\x01'
COMMAND_LIDAR_SET_MOTOR_PWM = b'\x02'

READINGS_LENGTH = 512


class I2C_master(object):
    def __init__(self, tcp_server):
        self.tcp_server = tcp_server
        self.i2c = I2C(0, scl=Pin(18), sda=Pin(19), freq=100000) #For hardware I2C
        #i2c = SoftI2C(scl=Pin(18), sda=Pin(19), freq=5000, timeout=255) #For software I2C
        self.i2c_lock = uasyncio.Lock()
        self.lidar = I2C_lidar(self)
        self.drivetrain = I2C_drivetrain(self)
        uasyncio.create_task(self.i2c_master_routine())
        uasyncio.create_task(self.i2c_drivetrain_routine())
        
    async def i2c_master_routine(self):
        while True:
            reading = await self.lidar.getRawLidarReadings(10)
            if reading != None:
                self.tcp_server.setRawLidarReadings(reading)
            await uasyncio.sleep_ms(5)

    async def i2c_drivetrain_routine(self):
        while True:
            await self.drivetrain.setDrivetrainSpeed()
            await uasyncio.sleep_ms(100)
        
    def getLock(self):
        return self.i2c_lock


class I2C_lidar(object):
    def __init__(self, i2c_master):
        self.i2c_master = i2c_master

    async def getRawLidarReadings(self, retries = 5):
        tries = 0
        b=bytearray(1)
        b[0] = 1
        #print(1, "Waiting for lock")
        await self.i2c_master.getLock().acquire()
        #print(1, "Lock acquired")
        while tries < retries: 
            try:
                self.i2c_master.i2c.writeto(0x42, b)
                #time.sleep(0.03) #needed or else freeze 
                await uasyncio.sleep_ms(50)
                break
            except OSError:
                tries+=1
                
        if tries >= retries:
            #print(1, "Releasing lock")
            self.i2c_master.getLock().release()
            return None

        tries = 0
        read = None
        while tries < retries:
            try:
                read = self.i2c_master.i2c.readfrom(0x42, 4*READINGS_LENGTH)
                break
            except OSError:
                tries+=1
        #print(1, "Releasing lock")
        self.i2c_master.getLock().release()
        return read

    async def setLidarMotorPwm(self, pulse_width_percent, retries = 10):
        tries = 0
        b=bytearray(1)
        b[0] = 2
        data = bytearray(2)
        data[0] = pulse_width_percent
        data[1] = pulse_width_percent >> 8
        #print(2, "Waiting for lock")
        await self.i2c_master.getLock().acquire()
        await uasyncio.sleep_ms(200) #waiting dor I2C line to be ready
        while tries < retries: 
            try:
                self.i2c_master.i2c.writeto(0x42, b)
                #time.sleep(0.03) #needed or else freeze 
                await uasyncio.sleep_ms(50)
                break
            except OSError:
                tries+=1

        if tries >= retries:
            print("Failed to write lidar pwm over I2C")
            self.i2c_master.getLock().release()
            return None

        tries = 0
        while tries < retries:
            try:
                self.i2c_master.i2c.writeto(0x42, data)
                await uasyncio.sleep_ms(50)
                break
            except OSError:
                tries+=1
       
        self.i2c_master.getLock().release()
        

class I2C_drivetrain(object):
    def __init__(self, i2c_master):
        self.i2c_master = i2c_master
        self.leftSpeed = 0
        self.rightSpeed = 0

    async def setDrivetrainSpeed(self):
        leftSpeed = self.leftSpeed
        rightSpeed = self.rightSpeed
    
        if(leftSpeed < 0):
            if(leftSpeed == -32768): #short handles value from -32768 to +32767
                leftSpeed +=1
            leftSpeed = -leftSpeed
            leftSpeed |= 0b1000000000000000 #set the 16th bit to 1 to indicate that the value is supposed to be negative

        if(rightSpeed < 0):
            if(rightSpeed == -32768): #short handles value from -32768 to +32767
                rightSpeed +=1
            rightSpeed = -rightSpeed
            rightSpeed |= 0b1000000000000000 #set the 16th bit to 1 to indicate that the value is supposed to be negative

        data = bytearray([0, leftSpeed >> 8, leftSpeed, rightSpeed >>8, rightSpeed])
        

        tries = 0
        retries = 5
        b=bytearray(1)
        b[0] = 45
        await self.i2c_master.getLock().acquire()
        await uasyncio.sleep_ms(50) #waiting dor I2C line to be ready
        while tries < retries: 
            try:
                self.i2c_master.i2c.writeto(0x04, b)
                await uasyncio.sleep_ms(50)
                break
            except OSError:
                tries+=1

        if tries >= retries:
            print("Failed to set drivetrain speed over I2C")
            self.i2c_master.getLock().release()
            return None

        tries=0
        while tries < retries: 
            try:
                self.i2c_master.i2c.writeto(0x04, data)
                await uasyncio.sleep_ms(50)
                break
            except OSError:
                tries+=1

        if tries >= retries:
            print("Failed to set drivetrain speed over I2C")

        self.i2c_master.getLock().release()