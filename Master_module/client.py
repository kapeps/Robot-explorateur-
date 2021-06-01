import socket
import struct
import time
#from matplotlib import plt

#UDP_IP = "192.168.1.148"
#UDP_PORT = 5005
#MESSAGE = "Hello, World!"
#sock = socket.socket(socket.AF_INET, # Internet
#                     socket.SOCK_DGRAM) # UDP
#print ("UDP target IP:", UDP_IP)
#print ("UDP target port:", UDP_PORT)
#data = struct.pack("<HH", 1, 1)
#sock.sendto(data, (UDP_IP, UDP_PORT))

TCP_IP = "192.168.1.148"
TCP_PORT = 5006
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((TCP_IP, TCP_PORT))

data = struct.pack("<H", 1) #start raw lidar readings stream
sock.send(data)
print("Data sent")
recv = sock.recv(4) #readings message length
READINGS_LENGTH = struct.unpack_from("<H", recv)[0]
print(READINGS_LENGTH)



import matplotlib.pyplot as plt
import numpy as np

plt.ion()
fig, ax = plt.subplots()
x, y = [0 for i in range(READINGS_LENGTH)],[0 for i in range(READINGS_LENGTH)]
sc = ax.scatter(x,y)
plt.grid(True)
plt.xlim(-5,5)
plt.ylim(-5,5)
plt.draw()


while True:
    read = sock.recv(4*READINGS_LENGTH)
    print(len(read))
    if(len(read) == 4*READINGS_LENGTH):
        for i in range(READINGS_LENGTH):
            heading = (read[4*i] + (read[4*i + 1] << 8))/64.0
            distance = (read[4*i + 2] + (read[4*i + 3] << 8))/4.0 /1000
            x[i] = distance*np.sin(heading * np.pi/180)
            y[i] = distance*np.cos(heading * np.pi/180)
    sc.set_offsets(np.c_[x,y])
    fig.canvas.draw_idle()
    plt.pause(0.1)

data = struct.pack("<H", 0) #stop raw lidar readings stream
sock.send(data)
print("Data sent")

plt.waitforbuttonpress()