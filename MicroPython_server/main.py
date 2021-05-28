import i2c_master
import time
import struct

import socket

import uasyncio

#my_ip = "192.168.4.1"
my_ip = "192.168.1.148"


UDP_IP = my_ip
UDP_PORT = 5005

TCP_PORT = 5006

tcp_clients = []

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

class tcp_client(object):
    def __init__(self,streamReader, streamWriter, tcp_server):
        self.streamReader = streamReader
        self.streamWriter = streamWriter
        self.shouldStreamLidar = False
        self.tcp_server = tcp_server
        uasyncio.create_task(self.recv_routine())

    async def recv_routine(self):
        while True:
            try:
                data = await self.streamReader.read(4)
                if len(data) > 0:
                    recv = struct.unpack("<H", data)

                    if recv[0] == 1:
                        self.shouldStreamLidar = True
                        answer = bytearray(4)
                        struct.pack_into("<H",answer, 0, i2c_master.READINGS_LENGTH)
                        self.streamWriter.write(answer)
                        await self.streamWriter.drain()
                        uasyncio.create_task(self.lidarReading_routine())

                    elif recv[0] == 0:
                        self.shouldStreamLidar = False
                await uasyncio.sleep_ms(5)

            except OSError:
                self.streamWriter.close()
                self.streamReader.close()
                print("Connection closed")
                break


    async def lidarReading_routine(self):
        while self.shouldStreamLidar:
            try:
                rawLidar = self.tcp_server.getRawLidarReadings()
                if(self.shouldStreamLidar):
                    if(rawLidar != None):
                        self.streamWriter.write(rawLidar)
                        await self.streamWriter.drain()
                await uasyncio.sleep_ms(200)
            except OSError:
                self.streamWriter.close()
                self.streamReader.close()
                print("Connection closed")
                break

class tcp_server(object):
    def __init__(self):
        self.rawLidarReadings = None
        self.server = uasyncio.start_server(self.tcp_callback, my_ip, TCP_PORT, backlog=5)
        uasyncio.create_task(self.i2c_routine())
        uasyncio.create_task(self.server)

    def getRawLidarReadings(self):
        return self.rawLidarReadings

    async def tcp_callback(self, streamReader, streamWriter):
        print("New accepted connection")
        tcp_client(streamReader, streamWriter, self)
    
    async def i2c_routine(self):
        while True:
            reading = await i2c_master.getRawLidarReadings(10)
            if reading != None:
                self.rawLidarReadings = reading
            await uasyncio.sleep_ms(5)


    


async def main():
    server = tcp_server()
    print("Ready")
    while True:
        await uasyncio.sleep_ms(1000)



uasyncio.run(main())
print("End of main")