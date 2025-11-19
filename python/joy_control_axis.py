exec(open('/choreonoid_ws/install/share/irsl_choreonoid/sample/irsl_import.py').read())

import rospy
from IPython.display import display
import ipywidgets as widgets
from threading import Lock

from sensor_msgs.msg import Joy

# out = widgets.Output()
# display(out)

class JoyControl(object):
    def __init__(self, scale_pos=0.01, scale_rot=0.05):
        self.lock = Lock()
        self.ax = mkshapes.make3DAxis(radius=0.04, length=0.3, axisRatio=0.25)
        self.di = DrawInterface()
        self.di.addObject(self.ax)
        self.sclp = scale_pos
        self.sclr = scale_rot
    #
    def callback_msg(self, msg):
        with self.lock:
            #out.append_stdout('out\n')
            #out.append_stdout('out: ' + msg + '\n')
            #rospy.loginfo(f'info: {msg}') ## see /rosout
            pos = fv(msg.axes[1], -msg.axes[0], msg.axes[2])
            rpy = fv(msg.axes[3],  msg.axes[4], msg.axes[5])
            pos *= self.sclp
            rpy *= self.sclr
            cds = coordinates(pos)
            cds.setRPY(rpy)
            ##
            self.ax.transform(cds)
    #
    def main(self):
        rospy.init_node('testjoy', anonymous=False)
        self.sub = rospy.Subscriber('sp_joy', Joy,
                                    callback=self.callback_msg, queue_size=1)

jc = JoyControl()
jc.main()
