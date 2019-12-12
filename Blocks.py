from math import pi
import logging

class Block():

    def __init__(self):

        #self.csys = [0.6,0,0.3,0,pi,0]
        logging.debug("creating Block")
        self.csys = [0,0,0,0,0,0]
        self.coordinates = []
        #self.tcp = [0,0,0,0,pi,0]  # this is not used atm, TCP is set inside the Program class
        self.a = 0.1
        self.v = 0.1
        self.radius = 0.03
        self.command = "movel"






