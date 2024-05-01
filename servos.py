from adafruit_servokit import ServoKit 
import logging


logger = logging.getLogger(__name__)

class Servos:

  currentPositions = list()
  servoSettings    = [
    #p-min, p-max, dir, default  
    [610,  1770, 1, 100],  # left arm
    [1750, 2850, 0, 0],    # right arm
    [1000, 2600, 0, 0],    # bottom neck
    [1000, 2500, 1, 0],    # top neck
    [350,  2400, 1, 50],   # head
    [1550, 2000, 1, 100],  # left eye
    [1000, 1450, 0, 0],    # right eye
    [1500, 2000, 0, 0],    # left eyebrow
    [900,  1550, 1, 100]   # right eyebrow
  ]

  def __init__(self):
    logger.info("Servo init")

    self.servoKit = ServoKit(channels=16)

    for index, servo in enumerate(self.servoSettings):
      self.servoKit.servo[index].set_pulse_width_range(servo[0] , servo[1])
      self.servoKit.servo[index].actuation_range = 100
      self.servoKit.servo[index].angle = servo[3]
      self.currentPositions.append(servo[3])

  def servoDirMap(self, servo, pos):
    start, end = (100, 0) if self.servoSettings[servo][2] == 1 else (0, 100)
    return self.mapRange(pos, 0, 254, start, end)

  def mapRange(self, value, inMin, inMax, outMin, outMax):
    return outMin + int(((value - inMin) / (inMax - inMin)) * (outMax - outMin))
  
  def cleanup(self):
    logger.info("Servos stopped")

    for index, servo in enumerate(self.servoSettings):
      self.servoKit.servo[index].angle = None

  def armControl(self, arm="both", pos=0):
    mapLeft  = self.servoDirMap(0, pos)
    mapRight = self.servoDirMap(1, pos)
    
    if arm == "left":
      if self.currentPositions[0] == mapLeft:
        return
      
      self.servoKit.servo[0].angle = mapLeft
      self.currentPositions[0]     = mapLeft
      logger.debug(f"---SERVO-LEFT-ARM, pos: {pos}, mapped: {mapLeft}")
    elif arm ==  "right":
      if self.currentPositions[1] == mapRight:
        return
      
      self.servoKit.servo[1].angle = mapRight
      self.currentPositions[1]     = mapRight
      logger.debug(f"---SERVO-RIGHT-ARM, pos: {pos}, mapped: {mapLeft}")
    elif arm ==  "both":
      if self.currentPositions[0] == mapLeft and self.currentPositions[1] == mapRight:
        return
      
      self.servoKit.servo[0].angle = mapLeft
      self.servoKit.servo[1].angle = mapRight
      self.currentPositions[0]     = mapLeft
      self.currentPositions[1]     = mapRight
      logger.debug(f"---SERVO-BOTH-ARM, pos: {pos}, mappedLeft: {mapLeft}, mappedRight: {mapRight}")

  def neckControl(self, neck="both", pos=0):
    mapBottom = self.servoDirMap(2, pos)
    mapTop    = self.servoDirMap(3, pos)
    
    if neck == "bottom":
      if self.currentPositions[2] == mapBottom:
        return
      
      self.servoKit.servo[2].angle = mapBottom
      self.currentPositions[2]     = mapBottom
      logger.debug(f"---SERVO-BOTTOM-NECK, pos: {pos}, mapped: {mapBottom}")
    elif neck ==  "top":
      if self.currentPositions[3] == mapTop:
        return
      
      self.servoKit.servo[3].angle = mapTop
      self.currentPositions[3]     = mapTop
      logger.debug(f"---SERVO-TOP-NECK, pos: {pos}, mapped: {mapTop}")
    elif neck ==  "both":
      if self.currentPositions[2] == mapBottom and self.currentPositions[3] == mapTop:
        return
      
      self.servoKit.servo[2].angle = mapBottom
      self.servoKit.servo[3].angle = mapTop
      self.currentPositions[2]     = mapBottom
      self.currentPositions[3]     = mapTop
      logger.debug(f"---SERVO-BOTH-NECK, pos: {pos}, mappedBottom: {mapBottom}, mappedTop: {mapTop}")

  def headControl(self, pos=0):
    mapped = self.servoDirMap(4, pos)
    
    if self.currentPositions[4] == mapped:
      return
    
    self.servoKit.servo[4].angle = mapped
    self.currentPositions[4]     = mapped
    logger.debug(f"---SERVO-HEAD, pos: {pos}, mapped: {mapped}")

  def eyeControl(self, eye="both", pos=0):
    mapLeft  = self.servoDirMap(5, pos)
    mapRight = self.servoDirMap(6, pos)
    
    if eye == "left":
      if self.currentPositions[5] == mapLeft:
        return
      
      self.servoKit.servo[5].angle = mapLeft
      self.currentPositions[5]     = mapLeft
      logger.debug(f"---SERVO-LEFT-EYE, pos: {pos}, mapped: {mapLeft}")
    elif eye ==  "right":
      if self.currentPositions[6] == mapRight:
        return
      
      self.servoKit.servo[6].angle = mapRight
      self.currentPositions[6]     = mapRight
      logger.debug(f"---SERVO-RIGHT-EYE, pos: {pos}, mapped: {mapRight}")
    elif eye ==  "both":
      if self.currentPositions[5] == mapLeft and self.currentPositions[6] == mapRight:
        return
      
      self.servoKit.servo[5].angle = mapLeft
      self.servoKit.servo[6].angle = mapRight
      self.currentPositions[5]     = mapLeft
      self.currentPositions[6]     = mapRight
      logger.debug(f"---SERVO-BOTH-EYE, pos: {pos}, mappedLeft: {mapLeft}, mappedRight: {mapRight}")

  def eyebrowControl(self, eye="both", pos=0):
    mapLeft  = self.servoDirMap(7, pos)
    mapRight = self.servoDirMap(8, pos)
    
    if eye == "left":
      if self.currentPositions[7] == mapLeft:
        return
      
      self.servoKit.servo[7].angle = mapLeft
      self.currentPositions[7]     = mapLeft
      logger.debug(f"---SERVO-LEFT-EYEBROW, pos: {pos}, mapped: {mapLeft}")
    elif eye ==  "right":
      if self.currentPositions[8] == mapRight:
        return
      
      self.servoKit.servo[8].angle = mapRight
      self.currentPositions[8]     = mapRight
      logger.debug(f"---SERVO-RIGHT-EYEBROW, pos: {pos}, mapped: {mapRight}")
    elif eye ==  "both":
      if self.currentPositions[7] == mapLeft and self.currentPositions[8] == mapRight:
        return
      
      self.servoKit.servo[7].angle = mapLeft
      self.servoKit.servo[8].angle = mapRight
      self.currentPositions[7]     = mapLeft
      self.currentPositions[8]     = mapRight
      logger.debug(f"---SERVO-BOTH-EYEBROW, pos: {pos}, mappedLeft: {mapLeft}, mappedRight: {mapRight}")




