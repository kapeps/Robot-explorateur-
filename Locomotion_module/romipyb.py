############
# romipyb.py for Micropython on Pyboard
#
# This module is a driver for the Romi chassis by Pololu, 
# equipped with the Motor driver and power distribution board.
#
# See https://www.pololu.com/category/202/romi-chassis-and-accessories
#
# © Frédéric Boulanger <frederic.softdev@gmail.com>
# 2020-04-02 -- 2020-05-24
# This software is licensed under the Eclipse Public License 2.0
############
import pyb
from pyb import Pin, Timer, ExtInt
from PID import PID
from myconstants import *

import micropython
# The following line is useful to debug error in IRQ callbacks
#micropython.alloc_emergency_exception_buf(100)

"""
This class is for driver one motor of the chassis and its rotation encoder
"""
class RomiMotor :
  """
  We reuse the same timer for all instances of the class, so this is the callback
  of the class, which calls the handlers in each instance.
  """
  @classmethod
  def class_rpm_handler(cls, tim) :
    for h in cls.rpm_handlers :
      h(tim)
  
  # List of the rpm handlers of the instances, necessary because we share a single timer.
  rpm_handlers = []
  # The shared timer
  rpmtimer = None
  
  """
  Initialize a RomiMotor, connected either to the 'X' side or the 'Y' side of the Pyboard.
  On either side (? is 'X' or 'Y'):
    - PWM is on pin ?1
    - DIR is on pin ?2
    - SLEEP is on pin ?3
    - ENCA is on pin ?4
    - ENCB is on pin ?5
  """
  def __init__(self, X=True) :
    if X :
      self.pwmpin = Pin('X6', Pin.OUT_PP)
      self.pwmtim = Timer(2, freq=5000)
      self.pwm = self.pwmtim.channel(1, mode=Timer.PWM, pin=self.pwmpin)
      self.pwm.pulse_width(0)
      self.dir = Pin('X2', Pin.OUT_PP)
      self.dir.off()          # O = forward, 1 = reverse
      self.sleep = Pin('X3', Pin.OUT_PP)
      self.sleep.value(0)        # 0 = sleep, 1 = active
      self.enca = Pin('X4', Pin.IN, Pin.PULL_UP)
      self.encb = Pin('X5', Pin.IN, Pin.PULL_UP)
    else :
      self.pwmpin = Pin('Y1', Pin.OUT_PP)
      self.pwmtim = Timer(8, freq=5000)
      self.pwm = self.pwmtim.channel(1, mode=Timer.PWM, pin=self.pwmpin)
      self.pwm.pulse_width(0)
      self.dir = Pin('Y2', Pin.OUT_PP)
      self.dir.off()          # O = forward, 1 = reverse
      self.sleep = Pin('Y3', Pin.OUT_PP)
      self.sleep.value(0)        # 0 = sleep, 1 = active
      self.enca = Pin('Y4', Pin.IN, Pin.PULL_UP)
      self.encb = Pin('Y5', Pin.IN, Pin.PULL_UP)
    self.pwmscale = (self.pwmtim.period() + 1) // 10000 # scale factot for permyriad(10000 as it allows to get more distinct points and avoid divisions) power
    self.count_a = 0      # counter for impulses on the A output of the encoder
    self.target_a = 0     # target value for the A counter (for controlled rotation)
    self.count_b = 0      # counter for impulses on the B output of the encoder
    self.time_a = 0       # last time we got an impulse on the A output of the encoder
    self.time_b = 0       # last time we got an impulse on the B output of the encoder
    self.elapsed_a_b = 0  # time elapsed between an impulse on A and an impulse on B
    self.dirsensed = 0    # direction sensed through the phase of the A and B outputs
    self.rpm = 0          # current speed in rotations per second
    self.rpm_last_a = 0   # value of the A counter when we last computed the rpms
    self.cruise_rpm = 0   # target value for the rpms
    self.walking = False  # Boolean that indicates if the robot is walking or stationary
    self.desiredDir = True# Boolean that indecates the desired direction of the motor for move function


    self._control = PID() # PID control for the rotation of the wheels
    self._control.setTunings(KP, KI, KD);
    self._control.setSampleTime(1);
    self._control.setOutputLimits(-10000, 10000)

    self._control_distance = PID() # PID control for the cascade of the distance
    self._control_distance.setTunings(KP_DISTANCE, KI_DISTANCE, KD_DISTANCE);
    self._control_distance.setSampleTime(1);
    self._control_distance.setOutputLimits(-MAXIMUM_VELOCITY, MAXIMUM_VELOCITY)


    ExtInt(self.enca, ExtInt.IRQ_RISING, Pin.PULL_UP, self.enca_handler)
    ExtInt(self.encb, ExtInt.IRQ_RISING, Pin.PULL_UP, self.encb_handler)
    if RomiMotor.rpmtimer is None :   # create only one shared timer for all instances
      RomiMotor.rpmtimer = Timer(4)
      RomiMotor.rpmtimer.init(freq=100, callback=RomiMotor.class_rpm_handler)
    RomiMotor.rpm_handlers.append(self.rpm_handler) # register the handler for this instance
  
  """
  Handler for interrupts caused by impulses on the A output of the encoder.
  This is where we sense the rotation direction and adjust the throttle to 
  reach a target number of rotations of the wheel.
  """
  def enca_handler(self, pin) :
    self.count_a += 1
    if self.encb.value():
      self.dirsensed = -1   # A occurs before B
    else :
      self.dirsensed = 1    # B occurs before A
    if self.target_a > 0 :  # If we have a target rotation      

      if self.count_a >= self.target_a :
        self.cruise_rpm = 0
        self.pwm.pulse_width(0)   # If we reached of exceeded the rotation, stop the motor
        self.target_a = 0         # remove the target
        self.walking = False

      else:                       # The cascade control for the distance
        self._control_distance.setSetPoint(self.target_a)
        self.cruise_rpm = self._control_distance.compute(self.count_a)
        self.walking = True

  
        

  """
  Handler for interrupts caused by impulses on the B output of the encoder.
  """
  def encb_handler(self, pin) :
    self.count_b += 1


  """
  This is the handler of the timer interrupts to compute the rpm
  """
  def rpm_handler(self, tim) :

    self.rpm =  100*(self.count_a - self.rpm_last_a)   # The timer is at 100Hz
    self.rpm_last_a = self.count_a      # Memorize the number of impulses on A
    
    if self.cruise_rpm != 0 :           # If we have an rpm target

      self._control.setSetPoint(self.cruise_rpm)
      output = self._control.compute(self.rpm)
      if output < 0 or self.desiredDir == False:  # Corrects the control output for the desired direction
        if output < 0:
          output = -output
        self.dir.off()
      else :
        self.dir.on()

      self.pwm.pulse_width(output * self.pwmscale) 
      self.walking = True
      self.sleep.on()
    else:
      self.walking = False
  
  """
  Set the power of the motor in percents.
  Positive values go forward, negative values go backward.
  """
  def throttle(self, pct) :
    if pct is None :
      return
    if pct < 0 :
      self.dir.off()
      pct = -pct
    else :
      self.dir.on()
    self.pwm.pulse_width(100 * pct * self.pwmscale)
    self.walking = True
    self.sleep.on()
  
  """
  Get the current power as a percentage of the max power.
  The result is positive if the motor runs forward, negative if it runs backward.
  """
  def getThrottle(self) :
    thr = self.pwm.pulse_width() // self.pwmscale
    if self.dir.value() > 0 :
      thr = -thr
    return thr
  
  """
  Release the motor to let it rotate freely.
  """
  def release(self, release=True) :
    if release :
      self.sleep.off()
    else :
      self.sleep.on()

  """
  Perform 'tics' 1/360 rotation of the wheel at 'power' percents of the max power.
  If 'turns' is positive, the wheel turns forward, if it is negative, it turns backward.
  """
  def rotatewheel(self, tics, power=20):
    if tics < 0 :
      self.desiredDir = False
      tics = -tics
    else :
      self.desiredDir = True
    self.count_a = 0
    self.count_b = 0
    self._control_distance.setOutputLimits(-power*100, power*100)
    self.target_a = int(tics)
  
  """
  Wait for the rotations requested by 'rotatewheel' to be done.
  """
  def wait(self) :
    while self.target_a !=0 :
      pass

  """
  Set a target rpms. The wheel turns in its current rotation direction,
  'rpm' should be non negative.
  """
  def cruise(self, rpm) :
    if rpm < 0 :
      self.desiredDir = False
      rpm = -rpm
    else :
      self.desiredDir = True    
    self.cruise_rpm = int(rpm * 6)
  
  """
  Get the current rpms. This is always non negative, regardless of the rotation direction.
  """
  def get_rpms(self) :
    return self.rpm / 60
  
  """
  Cancel all targets of rotation and rpm
  """
  def clear(self) :
    self.target_a = 0
    self.cruise_rpm = 0
    self.desiredDir = True
    self.rpm = 0
    self.rpm_last_a = 0
    self.count_a = 0
    self.count_b = 0
    self.pwm.pulse_width(0)

  """
  Stop the motor.
  """
  def stop(self) :
    self.clear()
    self.throttle(0)

"""
A class for controlling a Pololu Romi chassis equipped with the Motor driver and 
power distribution board.
"""
class RomiPlatform :
  """
  Create a controller for a chassis.
  The left motor should be connected to the 'X' pins.
  The right motor should be connected to the 'Y' pins.
  The control ('CTRL') pin of the chassis should be connected to pin X12
  """
  def __init__(self) :
    self.leftmotor = RomiMotor(X=False)
    self.rightmotor = RomiMotor(X=True)
    self.control = Pin('X12', Pin.OUT)
    self.control.value(1)
    
    
    self.switchLeft = Pin('X11', Pin.IN, Pin.PULL_UP)
    self.switchRight = Pin('X10', Pin.IN, Pin.PULL_UP)
    self.switchMiddle = Pin('Y12', Pin.IN, Pin.PULL_UP)
    self.MHsensorRight = Pin('Y11', Pin.IN, Pin.PULL_DOWN)
    self.MHsensorLeft = Pin('X9', Pin.IN, Pin.PULL_DOWN)
    self.timer = pyb.Timer(6,freq=1)
    self.timer.callback(self.sensorsCheck)
  
  def sensorsCheck(self,timer):
    if(not self.switchMiddle.value()) :
      self.middle_handler(1)
    if(not self.switchLeft.value() or self.MHsensorLeft.value()) :
      self.left_handler(1)  
    if(not self.switchRight.value() or self.MHsensorRight.value()) :
      self.right_handler(1)  

  """
  Function that decodes the I2C message and realizes the desired movement
  """
  def decodeI2CMessage(self,message):
    if (message[0] == 0) :
      desiredSpeedLeft = 0.0
      desiredSpeedRight = 0.0

      if ( (message[1] >> 7) & 1) : #it is a negative number
        desiredSpeedLeft = float(-message[2] - 256 * (message[1] & 0b01111111))/10
      else :#positive number
        desiredSpeedLeft = float(message[2] + 256 * message[1])/10
      
      if ( (message[3] >> 7) & 1) : #it is a negative number
        desiredSpeedRight = float(-message[4] - 256 * (message[3] & 0b01111111))/10
      else : #positive number
        desiredSpeedRight = float(message[4] + 256 * message[3])/10
      self.cruise(desiredSpeedLeft, desiredSpeedRight)



    elif (message[0] == 1) :
      distanceLeft = 0
      distanceRight = 0
      if  ( (message[1] >> 7) & 1) : #it is a negative number
        distanceLeft = -(int)(message[2]) - 256 * (message[1] & 0b01111111)
      else : #positive number
        distanceLeft = (int)(message[2]) + 256 * (message[1])
      if ( (message[3] >> 7) & 1) : #it is a negative number
        distanceRight = -(int)(message[4]) - 256 * (message[3] & 0b01111111);
      else : #//positive number
        distanceRight = (int)(message[4]) + 256 * (message[3]);
      self.move(distanceLeft, distanceRight)
    #print(message)



  """
  Handler for the interruption caused by the left switch, meaning an obstacle found in the left
  """
  def left_handler(self,pin):
    self.clear()
    self.leftMovementBack()


  """
  The action of backing up to the left
  """
  def leftMovementBack(self):
    self.leftmotor.pwm.pulse_width(100 * 50 * self.leftmotor.pwmscale)
    self.leftmotor.target_a = 100
    self.leftmotor.desiredDir = True
    self.leftmotor._control_distance.setOutputLimits(-2*100, 2*100)
    self.leftmotor.sleep.on()
    self.rightmotor.pwm.pulse_width(100 * 50 * self.rightmotor.pwmscale)
    self.rightmotor.target_a = 450
    self.rightmotor.desiredDir = True
    self.rightmotor._control_distance.setOutputLimits(-4*100, 4*100)
    self.rightmotor.sleep.on()

  """
  Handler for the interruption caused by the Right switch, meaning an obstacle found in the left
  """
  def right_handler(self,pin):
    self.clear()
    self.RightMovementBack()

  """
  The action of backing up to the right
  """
  def RightMovementBack(self):
    self.leftmotor.pwm.pulse_width(100 * 50 * self.leftmotor.pwmscale)
    self.leftmotor.target_a = 450
    self.leftmotor.desiredDir = True
    self.leftmotor._control_distance.setOutputLimits(-4*100, 4*100)
    self.leftmotor.sleep.on()
    self.rightmotor.pwm.pulse_width(100 * 50 * self.rightmotor.pwmscale)
    self.rightmotor.target_a = 100
    self.rightmotor.desiredDir = True
    self.rightmotor._control_distance.setOutputLimits(-2*100, 2*100)
    self.rightmotor.sleep.on()

  """
  Handler for the interruption caused by the middle switch, meaning an obstacle found in the left
  """
  def middle_handler(self,pin):
    self.clear()
    self.MiddleMovementBack()

  """
  The action of backing up to the left
  """
  def MiddleMovementBack(self):
    self.leftmotor.pwm.pulse_width(100 * 50 * self.leftmotor.pwmscale)
    self.leftmotor.target_a = 100
    self.leftmotor.desiredDir = True
    self.leftmotor._control_distance.setOutputLimits(-2*100, 2*100)
    self.leftmotor.sleep.on()
    self.rightmotor.pwm.pulse_width(100 * 50 * self.rightmotor.pwmscale)
    self.rightmotor.target_a = 450
    self.rightmotor.desiredDir = True
    self.rightmotor._control_distance.setOutputLimits(-4*100, 4*100)
    self.rightmotor.sleep.on()

  """
  Returns if the robot is walking or not
  """
  def isRobotWalking(self):
    return self.leftmotor.walking or self.rightmotor.walking

  """
  Set the throttle (power in percents) on the left and right motors.
  Positive power is forward, negative power is backward. Passing None keeps the 
  previous value for the power, so it is possible to change the power on only one motor.
  """
  def throttle(self, lpow, rpow) :
    self.leftmotor.throttle(lpow)
    self.rightmotor.throttle(rpow)
  
  """
  Get the power on the motors as a percentage of the maximum power.
  Positive power is forward, negative power is backward.
  """
  def getThrottle(self) :
    return (self.leftmotor.getThrottle(), self.rightmotor.getThrottle())

  """
  Make the wheels turn by a given number of turns, at 'power' percents of the 
  maximum power. 'ltics' and 'rtics' are always ints.
  Positive values turn forward, negative values turn backward.
  """
  def move(self, ltics, rtics, power=20) :
    self.clear()    
    start = True
    while(self.isRobotWalking() or start): 
      if (self.isRobotWalking()):
        start = False
      else:
        self.leftmotor.enca_handler(1)
        self.rightmotor.enca_handler(1)     
        self.leftmotor.rotatewheel(-ltics, power)
        self.rightmotor.rotatewheel(-rtics, power)
    self.clear()

    
    
  """
  Set a target rpm value for the wheels.
  The current rotation direction is preserved, only  the rotation speed is regulated.
  """
  def cruise(self, lrpms, rrpms) :
    self.clear()
    self.leftmotor.cruise(-lrpms)
    self.rightmotor.cruise(-rrpms)

  """
  Cancel all rotation and rpm targets.
  """
  def clear(self) :
    self.leftmotor.clear()
    self.rightmotor.clear()


  """
  Stop both motors.
  """
  def stop(self) :
    self.leftmotor.stop()
    self.rightmotor.stop()
  
  """
  Release both motors, let them turn freely.
  """
  def release(self, release=True) :
    self.leftmotor.release(release)
    self.rightmotor.release(release)
  
  """
  Shutdown the power on the chassis. This will also power down the ESP32 if 
  it is powered by the VCC MD pin of the chassis.
  """
  def shutdown(self) :
    # Drive the control pin low to shutdown the power of the platform
    self.control.value(0)

  """
  Power on the chassis.
  """
  def startup(self) :
    # Drive the control pin high to power the platform
    self.control.value(1)