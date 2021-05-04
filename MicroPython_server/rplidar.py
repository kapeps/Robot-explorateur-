from machine import UART
from machine import Pin
from machine import PWM
from uarray import array
import uselect as select
import ucollections as collections

import struct
import time
import _thread


START_FLAG_1 = b'\xA5'
START_FLAG_2 = b'\x5A'

#Request commands
COMMAND_STOP = b'\x25'
COMMAND_RESET = b'\x40'
COMMAND_SCAN = b'\x20'
COMMAND_EXPRESS_SCAN = b'\x82'
COMMAND_FORCE_SCAN = b'\x21'
COMMAND_GET_INFO = b'\x50'
COMMAND_GET_HEALTH = b'\x52'
COMMAND_GET_SAMPLERATE = b'\x59'
COMMAND_GET_LIDAR_CONF = b'\x84'

#Response descriptor
RESPONSE_DECRIPTOR_LENGTH = 7 #bytes



class RPLidarError(Exception):
    pass

class CommunicationError(RPLidarError):
    pass

class RPLidar(object):

    def __init__(self, id = 2, baudrate=115200, timeout=5000, motoctl = 13):
        self.uart = None
        self.motoctl = Pin(motoctl, Pin.OUT)
        self.motoPWM = PWM(self.motoctl)
        self.motoPWM.duty(0)
        self.connect(id, baudrate, timeout)

        self.readings_length = 400
        self._headings = array('H', [0 for i in range(self.readings_length)])
        self._distances = array('H', [0 for i in range(self.readings_length)])
        self._readings_index = 0
        self._descriptor_queue = collections.deque((), 32)
        self._next_data_type = None

        self._status = None
        self._error = None

    def connect(self, id, _baudrate, _timeout):
        self.uart = UART(id)
        self.uart.irq(UART.RX_ANY, priority = 5, handler = self._serial_handler)
        self.uart.init(baudrate = _baudrate, bits=8, parity=None, stop=1, timeout = _timeout, txbuf=512)
        self.set_motor_pwm()

    def disconnect(self):
        self.uart.deinit()
        self.set_motor_pwm(0)
        

    def _send_request(self, command):
        req = START_FLAG_1 + command
        self.uart.write(req)
        print('Command sent: %s' % req)

    def _read_response_descriptor(self):
        descriptor = self.uart.read(RESPONSE_DECRIPTOR_LENGTH)
        print('Recieved descriptor: ', descriptor)

        if(descriptor == None):
            print("Timeout")
            raise CommunicationError
        elif(len(descriptor) != RESPONSE_DECRIPTOR_LENGTH):
            print("Descriptor length mismatch")
            raise CommunicationError
        elif(not descriptor.startswith(START_FLAG_1 + START_FLAG_2)):
            print("Wrong descriptor starting bytes")
            raise CommunicationError

        data_response_lenght = int.from_bytes(descriptor[2:5], 'little') & ~(0b11<<28) #Remove 2btis from last byte that are reserved for send_mode

        send_mode = int.from_bytes(descriptor[5:6], 'little') & 0b11000000 #Extract the 2 bits from the byte
        is_single = send_mode == 0x0

        data_type = descriptor[6]

        print("Data response length : ", data_response_lenght)
        print("is single : ", is_single)
        print("data type : ", data_type)

        return data_response_lenght, is_single, data_type
    
    def _read_response(self, length):
        #print("Trying to read response: ",length," bytes")
        data = self.uart.read(length)
        #print('Recieved data: ', data)
        if data == None :
            print("Timout")
            raise CommunicationError
        if len(data) != length:
            print('Wrong body size')
            raise CommunicationError
        return data

    def _serial_handler(self):
        if(bool(self._descriptor_queue)): #if descriptor queue is not empty, expecting a response descriptor
            data_response_lenght, is_single, data_type = self._descriptor_queue.popleft()
            if self._read_response_descriptor() !=  (data_response_lenght, is_single, data_type):
                print("Unexpected response descirptor")
                raise CommunicationError
            self._next_data_type = data_type
            return
        
        elif self._next_data_type == 129: 
            data = self._read_response(5)

            S = data[0] & 0b00000001
            not_S = (data[0] & 0b00000010) >> 1
            C = data[1] & 0b00000001
            if S == not_S:
                print("Problem S = not_S")
                return
            #quality = data[0] >> 
            if C != 1:
                print("Problem C != 1")
                return
            
            distance_q2 = (data[3]) + (data[4] << 8)
            if distance_q2 != 0:
                #distance = distance_q2/4.0 #in mm
                #heading = ((data[1] >> 1) + (data[2] << 7))/64.0
                heading = ((data[1] >> 1) + (data[2] << 7))
                self._headings[self._readings_index] = heading
                self._distances[self._readings_index] = distance_q2
                
        elif self._next_data_type == 6:
            data = self._read_response(3)
            print(data[0:1])
            self._status = int.from_bytes(data[0:1], "little")
            self._error = int.from_bytes(data[1:2], "little")
            
        


    def set_motor_pwm(self, duty=600, freq=2^15-1):
        self.motoPWM.freq(freq)
        self.motoPWM.duty(duty)

    def get_health(self):
        self._status = None
        self._error = None
        self._send_request(COMMAND_GET_HEALTH)
        self._descriptor_queue.append((3, True, 6))

        while self._status == None or self._error == None:
            time.sleep(0.02)
        
        print("Status : ", self._status)
        print("Error : ", self._error)
        return self._status, self._error
            
    def stop(self):
        '''RPLIDAR will exit the current scanning state. 
            The laser diode and the measurement system will be disabled and the Idle state will be entered. 
            This request will be ignored when RPLIDAR is in the Idle or Protection Stop state.
            Since RPLIDAR won’t send response packet for this request, host systems should
            wait for at least 1 millisecond (ms) before sending another request'''
        print("Stopping scan")
        self.should_scan = False
        self._send_request(COMMAND_STOP)
        time.sleep(.002)
        if self.uart.any() > 0:
            print("Clearing buffer")
            data = self.uart.read() #clear uart buffer
            if data == None:
                print("Buffer was empty.....")

    def reset(self):
        '''A reset operation will make RPLIDAR revert to a similar state as it has just been
            powered up. This request is useful when RPLIDAR has entered the Protection Stop
            state. After a core reset, RPLIDAR will return to the idle state which will accept the
            start scan request again.
            Since RPLIDAR won’t send response packet for this request, host systems should
            wait for at least 2 milliseconds (ms) before sending another request. '''
        print("Resseting RPLidar")
        self._send_request(COMMAND_RESET)

    def start_scanning(self):
        self._send_request(COMMAND_SCAN)
        self._descriptor_queue.append((5, False, 129))
             


    def get_reading(self):
        reading = []
        for i in range(len(self._headings)):
            reading.append([self._headings[i]/64.0, self._distances[i]/4.0])
        return reading