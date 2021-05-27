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
        uasyncio.create_task(self.i2c_master_routine())
        
    async def i2c_master_routine(self):
        while True:
            reading = await self.lidar.getRawLidarReadings(10)
            if reading != None:
                self.tcp_server.setRawLidarReadings(reading)
            await uasyncio.sleep_ms(5)
        
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
        print(2, "Lock acquired")
        while tries < retries: 
            try:
                self.i2c_master.i2c.writeto(0x42, b)
                #time.sleep(0.03) #needed or else freeze 
                await uasyncio.sleep_ms(50)
                break
            except OSError:
                tries+=1

        if tries >= retries:
            print(2, "Failed")
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
        #print(2, "Releasing lock")
        self.i2c_master.getLock().release()
        


    #def getLidarReadings(retries = 5):
    #    
    #    read = getRawLidarReadings(retries)
    #    if read == None:
    #        return None
    #
    #    reading = []
    #    for i in range(READINGS_LENGTH):
    #        reading.append( [(read[4*i] + (read[4*i + 1] << 8))/64.0, (read[4*i + 2] + (read[4*i + 3] << 8))/4.0] )
    #
    #    return reading

        
        



