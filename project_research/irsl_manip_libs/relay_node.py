import rospy
import io
from threading import Lock

from irsl_iceoryx2 import SubIce
from irsl_iceoryx2 import PubIce

## toROS
class relayToROS(SubIce):
    def __init__(self, ice_name, topic_name, msg_class):
        super().__init__(ice_name)
        self.topic_name = topic_name
        self.msg_class  = msg_class
        self.queue_size = 1
        self.lock = Lock()
    #
    def _getLastMsg(self): ## non blocking receiving data
        buf = self.getLastData()
        if buf is None:
            return
        msg = msg_class()
        msg.deserialize(buf)
        self.pub.publish(msg)
    #
    def _getAllMsg(self):
        while self.has_samples():
            buf = self.getData()
            if buf is None:
                return
            msg = msg_class()
            msg.deserialize(buf)
            self.pub.publish(msg)
    #
    def timer_callback(self, event):
        self.getLastMsg()
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

class sendToROS(PubIce):
    def __init__(self, ice_name, msg_class):
        super.__init__(ice_name)
        self.msg_class = msg_class

    def sendMsg(self, msg):
        ## type check
        buf = io.BytesIO()
        msg.serialize(buf)
        self.sendData(buf)

## fromROS
class relayFromROS(PubIce):
    def __init__(self, ice_name, topic_name, msg_class, queue_size=1):
        super().__init__(ice_name)
        self.topic_name = topic_name
        self.msg_class = msg_class
        self.queue_size = queue_size
        self.lock = Lock()
    #
    def handle_msg(self, msg):
        with self.lock:
            buf = io.BytesIO()
            msg.serialize(buf)
            self.sendData(buf)
            return msg
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

class recvFromROS(SubIce):
    def __init__(self, ice_name, msg_class):
        super().__init__(ice_name)
        self.msg_class = msg_class

    def getMsg(self):
        buf = self.getData()
        if buf is None:
            return None
        msg = self.msg_class()
        return msg.deserialize(buf.getvalue())

    def getLastMsg(self):
        buf = self.getLastData()
        if buf is None:
            return None
        msg = self.msg_class()
        return msg.deserialize(buf.getvalue())
