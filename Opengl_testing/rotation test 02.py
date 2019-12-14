import numpy as np
import math3d
import urx

pose = [1, 2, 3, np.pi, -np.pi /2 , 0]
transform = math3d.Transform(pose)
transform2 = math3d.Transform()
transform2.pos.x = pose[0]
transform2.pos.y = pose[1]
transform2.pos.z = pose[2]
transform2.orient.rotate_xt(pose[3])
transform2.orient.rotate_yt(pose[4])
transform2.orient.rotate_zt(pose[5])

"""rint(np.array(pose))
print(transform.pose_vector)
print(transform2.pose_vector)
b= np.array(pose)[3]
b_1 = transform.pose_vector [3]
print(b/b_1)
#print(transform.orient.axis_angle)"""
'''
robot= urx.Robot("192.168.178.49")
pose = robot.get_pose()
pose_l = robot.getl()
print(pose_l)
#print(pose)
print(pose.pose_vector)
'''

#new_orient = math3d.Orientation()
new_orient = math3d.Orientation.new_euler(pose[3:], encoding='zyx')
print(new_orient)
new_vec = math3d.Vector(pose[:3])
new_trans = math3d.Transform(new_orient,new_vec)

print(new_trans.pose_vector)
#print(new_trans)