from drone import Drone
from color_format import basicConfig
from logging import getLogger, DEBUG

logger = getLogger()
logger.setLevel(DEBUG)
basicConfig(logger)

current = Drone()

current.queue_state("takeoff")
current.queue_state("patrol")
current.queue_state("landing")

current.start()
