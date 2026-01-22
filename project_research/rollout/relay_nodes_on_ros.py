import sys
sys.path.append('/opt/python')

import relay_node
# from relay_node import relayToROS
# from relay_node import relayFromROS
from relay_numpy_node import relayToROS
from relay_numpy_node import relayFromROS

import numpy as np

import rospy
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from sensor_msgs.msg import Image, JointState
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
from control_msgs.msg import JointTrajectoryControllerState

from cv_bridge import CvBridge

# ★ RobotInterface の読み込み（あなたの環境と同じやり方）
exec(open('/choreonoid_ws/install/share/irsl_choreonoid/sample/irsl_import.py').read())
ri = RobotInterface('/choreonoid_ws/src/irsl_hsr_pkgs/irsl_hsr_model/hsrb/robot_interface.yaml',
                    connection=True)
def array_to_jointtraj(ary, joint_names, duration=1.0):
    """numpy → JointTrajectory"""
    traj = JointTrajectory()
    traj.joint_names = joint_names

    point = JointTrajectoryPoint()
    point.positions = ary.tolist()
    point.time_from_start = rospy.Duration(duration)

    traj.points = [point]
    return traj

def image_msg_to_array(msg):
    bridge = CvBridge()
    cv_img = bridge.imgmsg_to_cv2(msg)
    return cv_img

STATE_JOINT_ORDER = [
    "LINK_0",
    "LINK_1",
    "LINK_2",
    "LINK_3",
    "LINK_4",
    "LINK_5",
    "LINK_6",
]
def joint_states_msg_to_array(msg):
    # name → index
    name_to_idx = {name: i for i, name in enumerate(msg.name)}

    vals = []
    for n in STATE_JOINT_ORDER:
        if n in name_to_idx:
            vals.append(msg.position[name_to_idx[n]])
        else:
            # 念のため無いときは0で埋める
            vals.append(0.0)

    return np.asarray(vals, dtype="float32")


##
##
##

# hand_image
r_hand_image = relayFromROS(
    'ice_hand_image',
    '/hsrb/hand_camera/image_raw',
    Image,
    hand_image_msg_to_array,
)

# joint_states
r_joint_states = relayFromROS(
    'ice_joint_states',
    '/hsrb/joint_states',
    JointState,
    joint_states_msg_to_array,
)


##
##
##
ARM_JOINT_NAMES  = [
    "LINK_0",
    "LINK_1",
    "LINK_2",
    "LINK_3",
    "LINK_4",
    "LINK_5",
]
_duration = 0.4
r_arm_cmd_out = relayToROS(
    'ice_arm_cmd_out',
    '/hsrb/arm_trajectory_controller/command',
    JointTrajectory,
    lambda ary: array_to_jointtraj(ary, ARM_JOINT_NAMES, _duration)
)

GRIPPER_JOINT_NAMES = ['LINK_6']
r_gripper_cmd_out = relayToROS(
    'ice_head_cmd_out',
    '/hsrb/head_trajectory_controller/command',
    JointTrajectory,
    lambda ary: array_to_jointtraj(ary, GRIPPER_JOINT_NAMES, _duration)
)

##
r_hand_image.main('irsl_relay_hand_image')       # ★ 追加
r_joint_states.main('irsl_relay_joint_states')    # ★ 追加

##
r_arm_cmd_out.main('relay_arm_cmd_out')
r_gripper_cmd_out.main('relay_gripper_cmd_out')

rospy.spin()
