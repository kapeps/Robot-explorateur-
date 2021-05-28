from pyb import I2C
from uarray import array


READINGS_LENGTH = 512 #length of the arrays containing the headings and distances

MAX_TXRETRIES = 5 #If failed 5 times to send the tx buffer, will stop trying

class I2C_Bus_error(Exception):
    pass

class tx_buffer_overflow(I2C_Bus_error):
    pass

class I2C_bus(object):

    def __init__(self, id=1, addr=0x42):
        self._id = id
        self._addr = addr
        self.i2c = I2C(self._id)
        self.i2c.init(I2C.SLAVE, addr=self._addr)
        self._txbuffer = bytearray(4 * READINGS_LENGTH)
        self._txsendretries = 0
        self._mv_txbuffer = memoryview(self._txbuffer) #pointer for speed optimization, slicing will not create a new buffer
        self._headings_mv = None
        self._distance_mv = None
        self._send_mode = 0
        self._num_in_txbuff = 0
        self._rxbuffer = bytearray(32)
        self._mv_rxbuffer = memoryview(self._rxbuffer) #pointer for speed optimization, slicing will not create a new buffer

    def update(self):
        if(self._send_mode == 1):
            try:
                recv = bytearray(1)
                self.i2c.recv(recv, timeout=200) #timeout in milliseconds
                if(recv[0] == 1):
                    for i in range(READINGS_LENGTH):
                        self._txbuffer[4*i] = self._headings_mv[i]
                        self._txbuffer[4*i + 1] = self._headings_mv[i] >> 8
                        self._txbuffer[4*i + 2] = self._distance_mv[i]
                        self._txbuffer[4*i + 3] = self._distance_mv[i] >> 8

                    self._num_in_txbuff = 4*READINGS_LENGTH
                    self._txsendretries = 0

            except OSError:
                pass

        if(self._num_in_txbuff > 0):
            try:
                self.i2c.send(self._mv_txbuffer[0:self._num_in_txbuff], timeout=500) #timeout in milliseconds
                #self.i2c.send(self._txbuffer, timeout=500)
                self._num_in_txbuff = 0
                self._txsendretries = 0
            except OSError:
                self._txsendretries += 1
                if(self._txsendretries > MAX_TXRETRIES):
                    self._num_in_txbuff = 0

    def setLidarMemoryViews(self, headings_view, distances_view):
        self._headings_mv = headings_view
        self._distance_mv = distances_view

    def sendLidarReadings(self):
        self._send_mode = 1