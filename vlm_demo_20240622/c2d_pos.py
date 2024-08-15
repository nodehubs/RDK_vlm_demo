import os
import sys
import argparse
from PIL import Image, ImageEnhance
import cv2
import numpy as np
import rospy
from sensor_msgs.msg import PointCloud2, Image, CameraInfo
from geometry_msgs.msg import TwistStamped
import ros_numpy

mid_pot = np.array([428,400])
# depth_K = np.array([459.1751708984375, 0.0, 322.4620056152344, 0.0, 458.2672119140625, 183.14112854003906, 0.0, 0.0, 1.0])
# depth_K = np.array([388.3108825683594, 0.0, 319.58514404296875, 0.0, 388.3108825683594, 239.42723083496094, 0.0, 0.0, 1.0])
depth_K = [381.47540283203125, 0.0, 314.031005859375, 0.0, 381.17864990234375, 241.7987823486328, 0.0, 0.0, 1.0]
c2d_R = np.array([[ 1.02380697, -0.01355805],[ 0.00819914,  1.06201602]])
c2d_k = [[0.027],[-2.124]]

def c2d_trans(img_depth, color_pos):
    # pos = c2d_R @ [[color_pos[0]],[color_pos[1]]] + c2d_k
    pos = color_pos
    pz = img_depth[int(pos[0])-1:int(pos[0])+2, int(pos[1])-1:int(pos[1])+2] / 1000
    pz = pz[pz>0]
    if not pz.shape[0]:
        return np.array([0,0,0], dtype=np.float32)
    pz = np.min(pz)
    # print(img_depth[int(color_pos[0]),int(color_pos[1])],pz)
    fx = depth_K[0]
    cx = depth_K[2]
    fy = depth_K[4]
    cy = depth_K[5]
    px = (mid_pot[0] - cx) / fx * pz
    py = (mid_pot[1] - cy) / fy * pz
    
    return np.array([[pz],[px],[py]], dtype=np.float16)
    # if 1:
        # print(mid_pot[0],mid_pot[1])
        # print(px, py, pz)


