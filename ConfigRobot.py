from GlobalFunc import *
import numpy as np
import logging


class ConfigRobot(object):
    """docstring for ConfigRobot"""
    def __init__(self):
        super(ConfigRobot, self).__init__()
        self.d6 = 82.3 # this is used for the tool length FIXME
        self.d = np.array([0, 89.159, 0, 0, 109.15, 82.3])
        self.a = np.array([0, 0, -425, -392.2, 0, 0])
        # self.alpha = math.pi/180*np.array([-90, 0, 0, 0])
        # self.q_init = math.pi/180*np.array([0, 0, 0, 0])
        self.alpha = DegToRad(np.array([0, 90, 0, 90, 0, 0]))
        #self.q_init = DegToRad(np.array([94, -162, -30, -78, 93, -184]))
        self.q_init = DegToRad(np.array([0,-90,-90,-90,90,0]))
        #self.q_init = DegToRad(np.array([0, 0, 0, 0, 0, 0]))
        logging.debug("Created Robot with the following settings: ")
        logging.debug(vars(self))

    def get_q_init(self):  # this doesnt seem to be used anywhere
        return self.q_init