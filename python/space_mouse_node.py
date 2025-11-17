#!/usr/bin/env python

import rospy
from sensor_msgs.msg import Joy
from std_msgs.msg import Header
##
import pyspacemouse as psm

class SpaceMouse(object):
    def __init__(self, qsize=1, topic='sp_joy'):
        self.pub = rospy.Publisher(topic, Joy, queue_size=qsize)
        self.smdev = psm.open(dof_callback=self.callback)

    def callback(self, data):
        msg = Joy(header=Header(stamp=rospy.get_rostime()),
                  axes = (data.x,data.y,data.z,data.roll,data.pitch,data.yaw),
                  buttons = data.buttons)
        self.pub.publish(msg)

    def main(self, rate_val):
        self.rate = rospy.Rate(rate_val)
        while not rospy.is_shutdown():
            self.smdev.read()
            self.rate.sleep()

if __name__ == '__main__':
    rospy.init_node('spacemouse_joy', anonymous=False)
    rate_val = rospy.get_param('~rate', 2000)
    qsize = rospy.get_param('~queue_size', 1)

    sm = SpaceMouse(qsize=qsize, topic='sp_joy')

    sm.main(rate_val)
