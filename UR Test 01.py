import urx
from GlobalFunc import *



robot = urx.Robot("192.168.178.20")

pose = DegToRad(np.array([0,-90,-90,-90,90,0]))
pose2 = DegToRad(np.array([0,-90,0,-90,90,0]))

robot.movej(pose,acc=0.5,vel=0.1)
robot.movej(pose2,acc=0.5,vel=0.1)
