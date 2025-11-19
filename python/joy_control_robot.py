# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.18.1
#   kernelspec:
#     display_name: Choreonoid
#     language: python
#     name: choreonoid
# ---

# %%
exec(open('/choreonoid_ws/install/share/irsl_choreonoid/sample/irsl_import.py').read())

# %%
# import os
# os.environ['ROS_MASTER_URI'] = 'http://yyy.yyy.yyy.yyy:11311'
# os.environ['ROS_IP'] = 'xxx.xxx.xxx.xxx'
# os.environ['ROS_HOSTNAME'] = 'xxx.xxx.xxx.xxx'

# %%
import rospy
from IPython.display import display
import ipywidgets as widgets
from threading import Lock
from sensor_msgs.msg import Joy

# %%
out = widgets.Output()
display(out)

# %%
class JoyControl(object):
    def __init__(self, scale_pos=0.01, scale_rot=0.05, send_interval=0.2,
                 robot=None, ri=None):
        self.lock = Lock()
        self.ax = mkshapes.make3DAxis(radius=0.04, length=0.3, axisRatio=0.25)
        self.di = DrawInterface()
        self.di.addObject(self.ax)
        self.sclp = scale_pos
        self.sclr = scale_rot
        self.verbose = False
        self.robot = robot
        self.ri = ri
        if self.robot is not None:
            self.ax.newcoords(self.robot.arm.endEffector)
    #
    def callback_msg(self, msg):
        res = self.lock.acquire(blocking=False)
        if not res:
            out.append_stdout('locked\n')
            return
        self.locked_process(msg)
        self.lock.release()
    #
    def locked_process(self, msg):
        if self.verbose:
            out.append_stdout(f'out: {msg}\n')
            rospy.loginfo(f'info: {msg}') ## see /rosout
        pos = fv(msg.axes[1], -msg.axes[0], msg.axes[2])
        rpy = fv(msg.axes[3],  msg.axes[4], msg.axes[5])
        pos *= self.sclp
        rpy *= self.sclr
        cds = coordinates(pos)
        cds.setRPY(rpy)
        ##
        self.ax.transform(cds)
        ##
        self.IK(self.ax)
    #
    def IK(self, cds):
        if self.robot is not None:
            res = self.robot.arm.inverseKinematics(cds)
            if self.ri is not None:
                self.ri.sendAngleVector(self.robot.angleVector(), tm=send_interval)
    #
    def main(self):
        rospy.init_node('testjoy', anonymous=False)
        self.sub = rospy.Subscriber('sp_joy', Joy,
                                    callback=self.callback_msg, queue_size=1)

# %%
robot = RobotModel.loadModelItem('camera_hand.body')
robot.registerEndEffector('arm', ## end-effector
                          'LINK_6', ## tip-link
                          tip_link_to_eef=coordinates(fv(0, 0, 0.03), fv(0.5, 0.5, 0.5, -0.5)),
                          joint_list=robot.jointNames
                          )

# %%
jc = JoyControl(robot = robot)
jc.main()
