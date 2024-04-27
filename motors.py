import RPi.GPIO as GPIO
import logging
import time
from enum import Enum
from threading import Thread, Event


logger = logging.getLogger(__name__)



class MDir(Enum):
  FORWARD   = 1
  BACKWARD  = 2
  TURNLEFT  = 3
  TURNRIGHT = 4
  STOP      = 0

class Motors:
  mState  = MDir.STOP
  B_state = MDir.STOP
  mDelay  = 0.01
  mStart  = 20

  def __init__(self, pinEnable_A, pinIN1_A, pinIN2_A, pinEnable_B, pinIN1_B, pinIN2_B):
    logger.info("Motors init")

    self.ENA = pinEnable_A
    self.EN1 = pinIN1_A
    self.EN2 = pinIN2_A
    self.ENB = pinEnable_B
    self.EN3 = pinIN1_B
    self.EN4 = pinIN2_B

    GPIO.setup(self.ENA, GPIO.OUT)
    GPIO.setup(self.EN1, GPIO.OUT)
    GPIO.setup(self.EN2, GPIO.OUT)
    GPIO.setup(self.ENB, GPIO.OUT)
    GPIO.setup(self.EN3, GPIO.OUT)
    GPIO.setup(self.EN4, GPIO.OUT)
    
    GPIO.output(self.EN1, GPIO.LOW)
    GPIO.output(self.EN2, GPIO.LOW)
    GPIO.output(self.EN3, GPIO.LOW)
    GPIO.output(self.EN4, GPIO.LOW)

    self.SpeedA=GPIO.PWM(self.ENA, 1000)
    self.SpeedA.start(0)

    self.SpeedB=GPIO.PWM(self.ENB, 1000)
    self.SpeedB.start(0)

  def forward(self, speed=100):
    if self.mState == MDir.FORWARD:
      return
    
    self.mState = MDir.FORWARD

    GPIO.output(self.EN1, GPIO.LOW)
    GPIO.output(self.EN2, GPIO.HIGH)
    GPIO.output(self.EN3, GPIO.LOW)
    GPIO.output(self.EN4, GPIO.HIGH)

    self.setSpeed(100)

    logging.info(f"---MOTORS-FORWARD, speed: 100")
    
    
  def backward(self, speed=100):
    if self.mState == MDir.BACKWARD:
      return
    
    self.mState = MDir.BACKWARD

    GPIO.output(self.EN1, GPIO.HIGH)
    GPIO.output(self.EN2, GPIO.LOW)
    GPIO.output(self.EN3, GPIO.HIGH)
    GPIO.output(self.EN4, GPIO.LOW)

    self.setSpeed(100)

    logging.info(f"---MOTORS-BACKWARD, speed: 100")


  def turnleft(self, speed=100):
    if self.mState == MDir.TURNLEFT:
      return
    
    self.mState = MDir.TURNLEFT

    GPIO.output(self.EN1, GPIO.HIGH)
    GPIO.output(self.EN2, GPIO.LOW)
    GPIO.output(self.EN3, GPIO.LOW)
    GPIO.output(self.EN4, GPIO.HIGH)

    self.setSpeed(100)

    logging.info(f"---MOTORS-LEFT, speed: 100")

  def turnright(self, speed=100):
    if self.mState == MDir.TURNRIGHT:
      return
    
    self.mState = MDir.TURNRIGHT

    GPIO.output(self.EN1, GPIO.LOW)
    GPIO.output(self.EN2, GPIO.HIGH)
    GPIO.output(self.EN3, GPIO.HIGH)
    GPIO.output(self.EN4, GPIO.LOW)

    self.setSpeed(100)

    logging.info(f"---MOTORS-RIGHT, speed: 100")

  def stop(self):
    if self.mState == MDir.STOP:
      return
    
    self.mState = MDir.STOP
    self.setSpeed(0)

    GPIO.output(self.EN1, GPIO.LOW)
    GPIO.output(self.EN2, GPIO.LOW)
    GPIO.output(self.EN3, GPIO.LOW)
    GPIO.output(self.EN4, GPIO.LOW)

    logging.info(f"---MOTORS-STOP")

  def setSpeed(self, speed=100):
    self.SpeedA.ChangeDutyCycle(speed)
    self.SpeedB.ChangeDutyCycle(speed)
  

class MotorSpeed(Thread):
 
  def __init__(self, *args, **kwargs):
    super(MotorSpeed, self).__init__(*args, **kwargs)
    self._stop = Event()

  def stop(self):
    self._stop.set()

  def stopped(self):
    return self._stop.isSet()

  def run(self, speed):
    for x in range(self.mStart, speed):
      if self.stopped():
        return
      
      print(x)
      self.SpeedA.ChangeDutyCycle(x)
      self.SpeedB.ChangeDutyCycle(x)
      time.sleep(self.mDelay)
