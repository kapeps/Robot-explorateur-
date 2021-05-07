from machine import UART
from machine import Pin
from machine import PWM
from uarray import array
import uselect as select

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
        self._last_reading_length = 0
        self.should_scan = False

    def connect(self, id, _baudrate, _timeout):
        self.uart = UART(id)
        self.uart.init(baudrate = _baudrate, bits=8, parity=None, stop=1, timeout = _timeout, txbuf=512)
        self.set_motor_pwm()

    def disconnect(self):
        self.uart.deinit()
        self.set_motor_pwm(0)
        

    def _send_request(self, command):
        req = START_FLAG_1 + command
        self.uart.write(req)
        #print('Command sent: %s' % req)

    def _read_response_descriptor(self):
        descriptor = self.uart.read(RESPONSE_DECRIPTOR_LENGTH)
        #print('Recieved descriptor: ', descriptor)

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

        #print("Data response length : ", data_response_lenght)
        #print("is single : ", is_single)
        #print("data type : ", data_type)

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

    def set_motor_pwm(self, duty=600, freq=2^15-1):
        self.motoPWM.freq(freq)
        self.motoPWM.duty(duty)

    def get_health(self):
        self._send_request(COMMAND_GET_HEALTH)
        data_response_length, is_single, _ = self._read_response_descriptor()
        if(data_response_length != 3  or is_single != True):
            print("Unexpected response descirptor for get_health")
            raise CommunicationError
        
        data = self._read_response(data_response_length)
        status = data[0]
        error = int.from_bytes(data[1:2], "little")
        print("Status : ", status)
        print("Error : ", error)
        return status, error
            
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
        self.should_scan = True
        _thread.start_new_thread(self._scan, (0,))

    def _scan(self, _):
        current_headings = array('H', [0 for i in range(self.readings_length)])
        current_distances = array('H', [0 for i in range(self.readings_length)])

        while self.should_scan:
            i=0
            self._send_request(COMMAND_SCAN)
            data_response_length, is_single, _ = self._read_response_descriptor()
            if(data_response_length != 5 or is_single != False):
                print("Unexpected response descirptor for scan")
                raise CommunicationError
            
            firstHeading = None
            while firstHeading == None:
                    data = self._read_response(data_response_length)

                    S = data[0] & 0b00000001
                    not_S = (data[0] & 0b00000010) >> 1
                    C = data[1] & 0b00000001
                    if S == not_S:
                        #print("Problem S = not_S")
                        continue
                    #quality = data[0] >> 2

                    if C != 1:
                        #print("Problem C != 1")
                        continue
                    

                    distance_q2 = (data[3]) + (data[4] << 8)
                    if distance_q2 != 0:
                        #distance = distance_q2/4.0 #in mm
                        #heading = ((data[1] >> 1) + (data[2] << 7))/64.0
                        heading = ((data[1] >> 1) + (data[2] << 7))
                        firstHeading = heading
                        current_headings[i] = heading
                        current_distances[i] = distance_q2
                        i+=1

            last_heading = None
            went_round = False
            try:
                while last_heading == None or last_heading<firstHeading or went_round == False:
                    data = self._read_response(data_response_length)
                    S = data[0] & 0b00000001
                    not_S = (data[0] & 0b00000010) >> 1
                    C = data[1] & 0b00000001
                    if S == not_S:
                        #print("Problem S = not_S")
                        continue
                    #quality = data[0] >> 2
                    if C != 1:
                        #print("Problem C != 1")
                        continue
                    
                    if S == 1:
                        went_round = True
                    distance_q2 = (data[3]) + (data[4] << 8)
                    if distance_q2 != 0:
                        #distance = distance_q2/4.0 #in mm
                        #heading = ((data[1] >> 1) + (data[2] << 7))/64.0
                        heading = ((data[1] >> 1) + (data[2] << 7))
                        last_heading = heading
                        current_headings[i] = heading
                        current_distances[i] = distance_q2
                        i+=1
                self._last_reading_length = i

            except Exception as inst:
                print(type(inst))
                print("First heading : ", firstHeading)
                print("Last heading : ", last_heading)
                print("went round : ", went_round)
                print(" i : ", i)
                print("readings : ", current_headings)

            self._send_request(COMMAND_STOP)
            time.sleep(0.02)

            while self.uart.any() > 0:                
                self.uart.read(self.uart.any()) #clear uart buffer
                
            
            for i in range(self._last_reading_length):
                self._headings[i] = current_headings[i]
                self._distances[i] = current_distances[i]

    def get_reading(self):
        reading = []
        for i in range(self._last_reading_length):
            reading.append([self._headings[i]/64.0, self._distances[i]/4.0])
        return reading