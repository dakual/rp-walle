import RPi.GPIO as GPIO
import time, sys
from motors import Motors
from radio import Radio, Controller
from servos import Servos
import logging
import lcd


logging.basicConfig(
  level    = logging.INFO,
  format   = "%(asctime)s [%(levelname)s] %(message)s",
  handlers = [
    logging.StreamHandler(sys.stdout),
    logging.FileHandler("debug.log", mode="w"),
  ]
)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

IN1 = 23
IN2 = 24
ENA = 18
IN3 = 5
IN4 = 6
ENB = 13

motors     = Motors(ENA, IN1, IN2, ENB, IN3, IN4)
servos     = Servos()
radio      = Radio()
controller = Controller(motors, servos)



if __name__ == '__main__':
  try:
    logging.info("Wall-e started")
    while True:
      commands = radio.receive()
      controller.process(commands)
      time.sleep(0.01)
      
  except KeyboardInterrupt:
    logging.info("Exiting...")

    radio.stop()
    servos.cleanup()
    GPIO.cleanup()
    sys.exit()

  
