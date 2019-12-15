import math3d as m3d
from math import *
import numpy as np

pose = [0, 1, 2, np.pi, 0.5*np.pi, -np.pi]

pose_orient = m3d.Orientation(pose[3:])
print("pose", np.array(pose))
print("pose orient" , pose_orient.rotation_vector)
print("angular norm ", pose_orient.ang_norm)
print(pose_orient.to_euler('XYZ'))

trans = m3d.Transform(pose)

#print("____"*300)
print(np.array(pose))
print(trans.pose_vector)
print("____"*300)
print("axis angle: ", trans.orient.axis_angle)
print("to euler zyx angle: ", trans.orient.to_euler('zyx'))
print("to euler ZYX angle: ", trans.orient.to_euler('ZYX'))
print("to euler xyz angle: ", trans.orient.to_euler('xyz'))
print("to euler XYZ angle: ", trans.orient.to_euler('XYZ'))
print("to euler zxy angle: ", trans.orient.to_euler('zxy'))
print("to euler ZXY angle: ", trans.orient.to_euler('ZXY'))

print("___")
print(trans.matrix)
print("___")
#print(trans)
print("___")
print(trans.list)
print(trans.pos)
print(trans.orient.rotation_vector)