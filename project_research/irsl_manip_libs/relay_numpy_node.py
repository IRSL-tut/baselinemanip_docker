import rospy
import io
from threading import Lock

from irsl_iceoryx2 import recvNumpy
from irsl_iceoryx2 import sendNumpy

## toROS
class relayToROS(recvNumpy):
    def __init__(self, ice_name, topic_name, msg_class, function_array_to_msg):
        super().__init__(ice_name)
        self.topic_name = topic_name
        self.msg_class  = msg_class
        self.array_to_msg = function_array_to_msg
        self.queue_size = 1
        self.lock = Lock()
    #
    def _getLastMsg(self): ## non blocking receiving data
        ary = self.getLastAry()
        if ary is None:
            return
        msg = self.array_to_msg(ary)
        self.pub.publish(msg)
    #
    def _getAllMsg(self):
        while self.has_samples():
            seif._getLastMsg()
    #
    def timer_callback(self, event):
        self._getLastMsg()
    #
    def main(self, nodename='submessage', **kwargs):
        try:
            rospy.get_rostime()
        except:
            rospy.init_node(nodename, **kwargs)
        ##
        self.pub = rospy.Publisher(self.topic_name, self.msg_class,
                                   queue_size = self.queue_size)
        self.timer = rospy.Timer(rospy.Duration(0.0004), self.timer_callback)

## fromROS
class relayFromROS(sendNumpy):
    def __init__(self, ice_name, topic_name, msg_class, function_msg_to_array, queue_size=1):
        super().__init__(ice_name)
        self.topic_name = topic_name
        self.msg_class = msg_class
        self.msg_to_array = function_msg_to_array
        self.queue_size = queue_size
        self.lock = Lock()
    #
    def handle_msg(self, msg):
        with self.lock:
            ary = self.msg_to_array(msg)
            buf = io.BytesIO()
            self.sendAry(ary)
            return ary
    #
    def main(self, nodename='submessage', **kwargs):
        try:
            rospy.get_rostime()
        except:
            rospy.init_node(nodename, **kwargs)
        ##
        self.sub = rospy.Subscriber(self.topic_name, self.msg_class,
                                    callback = self.handle_msg,
                                    queue_size = self.queue_size)
