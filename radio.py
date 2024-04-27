from nrf24 import NRF24
import RPi.GPIO as GPIO
import spidev
from threading import Thread, Event
import time
import logging
from utils import Process
from motors import MDir

logger = logging.getLogger(__name__)

class Radio(Thread):
  pipes = [
    [0xE0, 0xE0, 0xF1, 0xF1, 0xE0], 
    [0xF1, 0xF1, 0xF0, 0xF0, 0xE0]
  ]

  connected   = False
  threshold   = 0.5
  receiveTime = 0
  currentTime = 0
  conCommands = [127,127,127,127,0,0,0,0,0,0,0,0,0,0]

  def __init__(self):
    Thread.__init__(self)

    logger.info("Radio init")

    self.event = Event()
    self.radio = NRF24(GPIO, spidev.SpiDev())
    self.radio.begin(0, 22)
    self.radio.setPayloadSize(14)
    self.radio.setRetries(7,4)
    self.radio.setChannel(0x76)
    self.radio.setDataRate(NRF24.BR_250KBPS)
    self.radio.setPALevel(NRF24.PA_HIGH)
    self.radio.setCRCLength(NRF24.CRC_8)
    self.radio.setAutoAck(True)
    self.radio.openReadingPipe(0, self.pipes[1])

  def run(self):
    self.radio.startListening()
    logger.info("Radio started")

    while not self.event.is_set():
      if (self.radio.available(0)):
        self.radio.read(self.conCommands)
        self.receiveTime = time.time()

        if self.connected == False:
          logger.info("Radio connected")

        self.connected = True

      self.currentTime = time.time()
      if (self.currentTime - self.receiveTime > self.threshold):
        self.conCommands = [127,127,127,127,0,0,0,0,0,0,0,0,0,0]

        if self.connected == True:
          logger.info("Radio diconnected")

        self.connected = False
      
  def stop(self):
    logger.info("Radio stopped")

    self.event.set()
    self.radio.powerDown()
    self.join()

  def getCommands(self):
    return self.conCommands


class Controller():
  pressed = False
  voice   = None

  def __init__(self, radio, motors, servos):
    self.radio  = radio
    self.motors = motors
    self.servos = servos

  def run(self):
    JLX, JLY, JRX, JRY, JLB, JRB, PTL, PTR, SWL, SWR, BL1, BL2, BR1, BR2 = self.radio.getCommands()

    if JLY > 127 and JLX == 127:
      self.motors.forward()
    elif JLY < 127 and JLX == 127:
      self.motors.backward()
    if JLX > 127 and JLY == 127:
      self.motors.turnright()
    elif JLX < 127 and JLY == 127:
      self.motors.turnleft()
    elif JLX == 127 and JLY == 127 and JRX == 127 and JRY == 127:
      self.motors.stop()

    # head and neck control
    if JRY > 127:
      nb = self.servos.mapRange(JRY, 127, 254, 0, 254)
      self.servos.neckControl("bottom", nb)
    elif JRY < 127:
      nt = self.servos.mapRange(JRY, 0, 127, 0, 254)
      self.servos.neckControl("top", nt)
    if JRX > 127:
      self.servos.headControl(JRX)
    elif JRX < 127:
      self.servos.headControl(JRX)
    elif JRX == 127 and JRY == 127:
      self.servos.headControl(127)


    if BR1 > 0 and self.pressed == False:
      self.servos.eyebrowControl("left", 254)

    if BR2 > 0 and self.pressed == False:
      self.servos.eyebrowControl("right", 254)

    if BR1 <= 0 and BR2 <= 0 and self.voice == None:
      self.servos.eyebrowControl("both", 0) 

    if self.voice == None:
      self.servos.eyeControl("both", PTR)
      self.servos.armControl("both", PTL)

    if BL1 > 0 and self.voice == None:
      self.servos.eyebrowControl("both", 240)
      self.servos.eyeControl("both", 254)
      self.servos.armControl("both", 254)

      self.voice = Process(('aplay', '--device=plughw:1,0', '--format=S16_LE', '/home/pi/walle.wav'))
      self.voice.register_callback(self.voiceCallback)

    # if BL1 <= 0 and voice == None:
    #   eyebrowControl("both", 0)

  def voiceCallback(self):
    self.voice = None


