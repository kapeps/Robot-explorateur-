from machine import Pin
from machine import I2C #pas de timeout pour le I2C hardware
from machine import SoftI2C #pas de timeout pour le I2C hardware
from uarray import array

import uasyncio

import time

READINGS_LENGTH = 512

i2c = I2C(0, scl=Pin(18), sda=Pin(19), freq=100000) #For hardware I2C
#i2c = SoftI2C(scl=Pin(18), sda=Pin(19), freq=5000, timeout=255) #For software I2C


async def getRawLidarReadings(retries = 5):
    b= bytearray(1)
    b[0] = 1
    tries = 0

    
    while tries < retries: 
        try:
            i2c.writeto(0x42, b)
            #time.sleep(0.03) #needed or else freeze 
            await uasyncio.sleep_ms(30)
            break
        except OSError:
            tries+=1
            

    if tries >= retries:
        return None

    tries = 0
    read = None
    while tries < retries:
        try:
            read = i2c.readfrom(0x42, 4*READINGS_LENGTH)
            break
        except OSError:
            tries+=1

    return read


def getLidarReadings(retries = 5):
    
    read = getRawLidarReadings(retries)
    if read == None:
        return None

    reading = []
    for i in range(READINGS_LENGTH):
        reading.append( [(read[4*i] + (read[4*i + 1] << 8))/64.0, (read[4*i + 2] + (read[4*i + 3] << 8))/4.0] )

    return reading

        
        



