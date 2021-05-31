import sys, pygame
import time
import numpy as np
from PIL import Image
import socket
import struct
import threading


pygame.init()


img = Image.open('background.png')
background = pygame.image.load("background.png")

img = np.array(img)
height, width, _ = img.shape


black = 0, 0, 0
blackPixel = pygame.Surface((1,1))
blackPixel.fill(black)
white = 255,255,255
whitePixel = pygame.Surface((1,1))
whitePixel.fill(white)


size = width, height

screen = pygame.display.set_mode(size)

lastFrameTime = time.time()
frameTime = 1/60
screenCenter = np.array([width/2, height/2])

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
lidarReading = []


scale = 100
def positionToScreen(pos):
    return np.array(pos) * scale

def screenToPostion(pos):
    return np.array(pos)/scale

def readSocket():
    global lidarReading
    while True:
        read = sock.recv(4*READINGS_LENGTH)
        if(len(read) == 4*READINGS_LENGTH):
            lidarReading = read
        time.sleep(0.001)

leftSpeed =  0
rightSpeed = 0
def writeSocket():
    global leftSpeed, rightSpeed
    while True:
        data = struct.pack("<H", 2) #send speeds
        sock.send(data)
        data = struct.pack("<hh", leftSpeed, rightSpeed) #start raw lidar readings stream
        #print(data)
        sock.send(data)
        time.sleep(0.1)



receiveThread = threading.Thread(target=readSocket)
receiveThread.start()

writeThread = threading.Thread(target=writeSocket)
writeThread.start()


def Update(deltaTime):
    readInputs()

def render(screen):
    global lidarReading, READINGS_LENGTH
    screen.blit(background, (0,0))
    if(len(lidarReading) == 4*READINGS_LENGTH):
        for i in range(READINGS_LENGTH):
            heading = ((lidarReading[4*i] + (lidarReading[4*i + 1] << 8))/64.0)*np.pi/180
            distance = (lidarReading[4*i + 2] + (lidarReading[4*i + 3] << 8))/4.0 /1000
            pointPos = positionToScreen(distance * np.array([np.cos(heading - 90), np.sin(heading - 90)]))
            drawPos = screenCenter + pointPos
            pygame.draw.circle(screen, (0,0,255), (int(drawPos[0]), int(drawPos[1])), 5)

    pygame.display.flip()

def readInputs():
    global leftSpeed, rightSpeed
    leftSpeed = 0
    rightSpeed = 0
   
    keys=pygame.key.get_pressed()
    scale = 1
    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
        scale = 2
    if keys[pygame.K_UP]:
        leftSpeed += scale*400
        rightSpeed += scale*400
    if keys[pygame.K_DOWN]:
        leftSpeed -= scale*400
        rightSpeed -= scale*400
        
    if keys[pygame.K_LEFT]:
        leftSpeed -= scale*200
        rightSpeed += scale*200
    if keys[pygame.K_RIGHT]:
        leftSpeed += scale*200
        rightSpeed -= scale*200
    

while True:
    for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_v:
                    print("Zooming in")
                    scale += 10
                elif event.key == pygame.K_b:
                    print("Zooming out")
                    scale -= 10

    deltaTime = time.time() - lastFrameTime
    if deltaTime >= frameTime:
        lastFrameTime = time.time()
        Update(deltaTime)
        render(screen)