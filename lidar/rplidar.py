from machine import UART
from machine import Pin
from uarray import array
import ucollections as collections
import time
import utime

print("Test")

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
SCAN_DATATYPE = 129 
SCAN_RESPONSE_LENGTH = 5 #bytes
GET_HEALTH_DATATYPE = 3
GET_HEALTH_RESPONSE_LENGTH = 6#bytes


READINGS_LENGTH = 512 #length of the arrays containing the headings and distances
RXBUFFER_LENGTH = 16384 #bytes


class RPLidarError(Exception):
    pass

class CommunicationError(RPLidarError):
    pass

class ScanningError(RPLidarError):
    pass

class RPLidar(object):

    def __init__(self, id = 2, baudrate=115200, timeout=5000, motoctl = 'x5'):
        self.uart = None
        #self.motoctl = Pin(motoctl, Pin.OUT)
        #self.motoctl.value(1)
        #self.motoPWM = PWM(self.motoctl)
        #self.motoPWM.duty(0)
        self.connect(id, baudrate, timeout)

        self._rxbuffer = bytearray(32)
        self._headings = array('H', [0 for i in range(READINGS_LENGTH)])#heading = heading[i]/64.0
        self._distances = array('H', [0 for i in range(READINGS_LENGTH)])#distance = distance[i]/4.0 #in mm
        self._readings_index = 0
        self._descriptor_queue = collections.deque((), 32) #File fifo
        self._next_data_type = None

        self._status = None
        self._error = None
        self._scanerrors = 0

    def connect(self, id, _baudrate, _timeout):
        self.uart = UART(id)
        self.uart.init(baudrate = _baudrate, bits=8, parity=None, stop=1, timeout = _timeout, read_buf_len=RXBUFFER_LENGTH)
        self.set_motor_pwm()

    def disconnect(self):
        self.uart.deinit()
        self.set_motor_pwm(0)
        

    def _send_request(self, command):
        if command == COMMAND_SCAN:
            self._descriptor_queue.append((SCAN_RESPONSE_LENGTH, False, SCAN_DATATYPE))
        elif command == COMMAND_GET_HEALTH:
            self._descriptor_queue.append((GET_HEALTH_RESPONSE_LENGTH, False, GET_HEALTH_DATATYPE))

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
        bytes_read = self.uart.readinto(self._rxbuffer, length)
        #print('Recieved data: ', self._rxbuffer)
        if bytes_read == None :
            print("Timout")
            raise CommunicationError
        if bytes_read != length:
            print('Wrong body size')
            raise CommunicationError

    def _serial_handler(self):

        if(bool(self._descriptor_queue)): #if descriptor queue is not empty, expecting a response descriptor
            data_response_lenght, is_single, data_type = self._descriptor_queue.popleft()
            if self._read_response_descriptor() !=  (data_response_lenght, is_single, data_type):
                print("Unexpected response descirptor")
                raise CommunicationError
            self._next_data_type = data_type
            return
        
        elif self._next_data_type == SCAN_DATATYPE: 
            self._read_response(SCAN_RESPONSE_LENGTH)

            S = self._rxbuffer[0] & 0b00000001
            not_S = (self._rxbuffer[0] & 0b00000010) >> 1
            C = self._rxbuffer[1] & 0b00000001
            if S == not_S:
                #print("Problem S = not_S")
                self._scanerrors += 1
                return
            #quality = data[0] >> 
            if C != 1:
                #print("Problem C != 1")
                self._scanerrors += 1
                return
            
            if(self._scanerrors > 10):#11 consecutive scan error, reseting lidar
                print("Many consecutive scan errors, reseting lidar")
                self.reset()
                self._scanerrors = 0
                self.start_scanning()
                return

            self._scanerrors = 0 #managed to read without error
            distance_q2 = (self._rxbuffer[3]) + (self._rxbuffer[4] << 8)
            if distance_q2 != 0:
                heading = ((self._rxbuffer[1] >> 1) + (self._rxbuffer[2] << 7))
                self._headings[self._readings_index] = heading
                self._distances[self._readings_index] = distance_q2
                self._readings_index += 1
                if(self._readings_index >= READINGS_LENGTH):
                    self._readings_index = 0
                
                
        elif self._next_data_type == 6:
            self._read_response(3)
            print(self._rxbuffer[0:1])
            self._status = int.from_bytes(self._rxbuffer[0:1], "little")
            self._error = int.from_bytes(self._rxbuffer[1:2], "little")
            
        


    def set_motor_pwm(self, duty=600, freq=2^15-1):
        #self.motoPWM.freq(freq)
        #self.motoPWM.duty(duty)
        pass

    def get_health(self):
        self._status = None
        self._error = None
        self._send_request(COMMAND_GET_HEALTH)

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
            self.uart.read() #clear uart buffer

    def reset(self):
        '''A reset operation will make RPLIDAR revert to a similar state as it has just been
            powered up. This request is useful when RPLIDAR has entered the Protection Stop
            state. After a core reset, RPLIDAR will return to the idle state which will accept the
            start scan request again.
            Since RPLIDAR won’t send response packet for this request, host systems should
            wait for at least 2 milliseconds (ms) before sending another request. '''
        print("Resseting RPLidar")
        self._send_request(COMMAND_RESET)
        time.sleep(1)
        if self.uart.any() > 0:
            print("Clearing buffer")
            self.uart.read(self.uart.any()) #clear uart buffer
        while bool(self._descriptor_queue):
            self._descriptor_queue.popleft()

    def start_scanning(self):
        self._send_request(COMMAND_SCAN)

    #Slow no preallocation
    def get_reading(self):
        reading = []
        for i in range(len(self._headings)):
            reading.append([self._headings[i]/64.0, self._distances[i]/4.0])
        return reading

    def get_headings_mv(self):
        return memoryview(self._headings)

    def get_distances_mv(self):
        return memoryview(self._distances)

    def update(self):
        inBuff = self.uart.any()
        if(inBuff > 0):            
            while  (bool(self._descriptor_queue) and inBuff >= RESPONSE_DECRIPTOR_LENGTH) or \
                (self._next_data_type == SCAN_DATATYPE and inBuff >= SCAN_RESPONSE_LENGTH) or \
                (self._next_data_type == GET_HEALTH_DATATYPE and inBuff >= GET_HEALTH_RESPONSE_LENGTH):
                    self._serial_handler()
                    inBuff = self.uart.any()