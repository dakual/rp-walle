from nrf24 import NRF24
import RPi.GPIO as GPIO
import spidev
import time
import logging
from utils import Process
from threading import Thread, Event

logger = logging.getLogger(__name__)

class Radio():
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
    logger.info("Radio init")

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
    self.radio.startListening()

    logger.info("Radio started")

  def receive(self):      
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

    return self.conCommands
      
  def stop(self):
    logger.info("Radio stopped")
    self.radio.powerDown()


class Controller():
  pressed = False
  voice   = None
  animationStarted = False
  BL2Pressed = False

  animation = [
    {"name":"h1", "servo": "head", "time": 0.005, "spos": 127, "epos": 200},
    {"name":"n1", "servo": "neck", "dir": "top", "time": 0.001, "spos": 245, "epos": 0, "delay": 0.1, "wait": "h1"},
    {"name":"a1", "servo": "arm", "dir": "right", "time": 0.005, "spos": 0, "epos": 180, "delay": 0.1, "wait": "h1"},
    {"name":"a2", "servo": "arm", "dir": "right", "time": 0.005, "spos": 180, "epos": 0, "delay": 0.5, "wait": "a1"},
    {"name":"n2", "servo": "neck", "dir": "top", "time": 0.005, "spos": 0, "epos": 254, "delay": 0.1, "wait": "a2"},
    {"name":"h2", "servo": "head", "time": 0.005, "spos": 200, "epos": 127, "delay": 0.1, "wait": "a2"},
    {"name":"h3", "servo": "head", "time": 0.005, "spos": 127, "epos": 54, "delay": 1, "wait": "h2"},
    {"name":"n3", "servo": "neck", "dir": "top", "time": 0.001, "spos": 245, "epos": 0, "delay": 0.1, "wait": "h3"},
    {"name":"a3", "servo": "arm", "dir": "left", "time": 0.005, "spos": 0, "epos": 180, "delay": 0.1, "wait": "h3"},
    {"name":"a4", "servo": "arm", "dir": "left", "time": 0.005, "spos": 180, "epos": 0, "delay": 0.5, "wait": "a3"},
    {"name":"n4", "servo": "neck", "dir": "top", "time": 0.005, "spos": 0, "epos": 254, "delay": 0.1, "wait": "a4"},
    {"name":"h4", "servo": "head", "time": 0.005, "spos": 54, "epos": 127, "delay": 0.1, "wait": "a4"},
    {"name":"n5", "servo": "neck", "dir": "bottom", "time": 0.002, "spos": 0, "epos": 254, "delay": 1, "wait": "h4"},
    {"name":"n7", "servo": "neck", "dir": "top", "time": 0.002, "spos": 254, "epos": 0, "delay": 1, "wait": "h4"},
    {"name":"e1", "servo": "eye", "dir": "both", "time": 0.001, "spos": 0, "epos": 254, "delay": 0.5, "wait": "n7"},
    {"name":"y1", "servo": "eyebrow", "dir": "both", "time": 0.0001, "spos": 0, "epos": 254, "delay": 0.1, "wait": "e1"},
    {"name":"y2", "servo": "eyebrow", "dir": "both", "time": 0.0001, "spos": 254, "epos": 0, "delay": 1, "wait": "y1"},
    {"name":"v1", "voice": "walle", "delay": 0.1, "wait": "e1"},  
    {"name":"e2", "servo": "eye", "dir": "both", "time": 0.001, "spos": 254, "epos": 0, "delay": 0.1, "wait": "y2"},
    {"name":"n8", "servo": "neck", "dir": "bottom", "time": 0.002, "spos": 254, "epos": 0, "delay": 0.1, "wait": "e2"},
    {"name":"n9", "servo": "neck", "dir": "top", "time": 0.002, "spos": 0, "epos": 254, "delay": 0.1, "wait": "e2"},
  ]

  def __init__(self, motors, servos):
    self.motors  = motors
    self.servos  = servos
    self.animationThreads = list()

  def process(self, commands):
    JLX, JLY, JRX, JRY, JLB, JRB, PTL, PTR, SWL, SWR, BL1, BL2, BR1, BR2 = commands

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

    # # head and neck control
    # if JRY > 127:
    #   nb = self.servos.mapRange(JRY, 127, 254, 0, 254)
    #   self.servos.neckControl("bottom", nb)
    # elif JRY < 127:
    #   nt = self.servos.mapRange(JRY, 0, 127, 0, 254)
    #   self.servos.neckControl("top", nt)
    # if JRX > 127:
    #   self.servos.headControl(JRX)
    # elif JRX < 127:
    #   self.servos.headControl(JRX)
    # elif JRX == 127 and JRY == 127:
    #   self.servos.headControl(127)


    # if BR1 > 0 and self.pressed == False:
    #   self.servos.eyebrowControl("left", 254)

    # if BR2 > 0 and self.pressed == False:
    #   self.servos.eyebrowControl("right", 254)

    # if BR1 <= 0 and BR2 <= 0 and self.voice == None:
    #   self.servos.eyebrowControl("both", 0) 

    # if self.voice == None:
    #   self.servos.eyeControl("both", PTR)
    #   self.servos.armControl("both", PTL)

    # if BL1 > 0 and self.voice == None:
    #   self.servos.eyebrowControl("both", 240)
    #   self.servos.eyeControl("both", 254)
    #   self.servos.armControl("both", 254)

    #   self.voice = Process(('aplay', '--device=plughw:1,0', '--format=S16_LE', '/home/pi/walle.wav'))
    #   self.voice.register_callback(self.voiceCallback)

  
    if BL2 > 0:
      if self.animationStarted or self.BL2Pressed:
        return
      
      self.animationStarted = True
      self.BL2Pressed       = True
      
      logger.info("Animation started")
      for i, v in enumerate(self.animation):
        x = Thread(name=v["name"], target=self.playAnimation, args=(v,))
        self.animationThreads.append(x)

      for th in self.animationThreads:
        th.start()

    elif BL2 <= 0:
      self.BL2Pressed = False

    # Animation controller
    if self.animationStarted:
      for index, thread in enumerate(self.animationThreads):
        if thread.is_alive():
          return
      self.animationStarted = False
      self.animationThreads = list()
      logger.info("Animation finished")

  def playAnimation(self, v):
    if "wait" in v:
      thread = self.getThreadByName(v["wait"])
      if thread != None:
        while thread.is_alive():
          time.sleep(0.1)

    if "delay" in v:
      time.sleep(v["delay"])

    if "servo" in v:
      logger.info(f"---%s animation", v["servo"])

      step = 1 if v["spos"] < v["epos"] else -1
      for x in range(v["spos"], v["epos"], step):
        if v["servo"] == "head":
          self.servos.headControl(x)
          time.sleep(v["time"])
        if v["servo"] == "neck":
          self.servos.neckControl(v["dir"], x)
          time.sleep(v["time"])
        if v["servo"] == "arm":
          self.servos.armControl(v["dir"], x)
          time.sleep(v["time"])
        if v["servo"] == "eye":
          self.servos.eyeControl(v["dir"], x)
          time.sleep(v["time"])
        if v["servo"] == "eyebrow":
          self.servos.eyebrowControl(v["dir"], x)
          time.sleep(v["time"])

    if "voice" in v:
      logger.info(f"---%s animation", v["voice"])

      self.voice = Process(('aplay', '--device=plughw:1,0', '--format=S16_LE', '/home/pi/walle.wav'))
      self.voice.register_callback(self.voiceCallback)

  def getThreadByName(self, name): 
    for index, thread in enumerate(self.animationThreads):
      if thread.name == name:
        return thread


  def voiceCallback(self):
    self.voice = None

