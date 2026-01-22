import rosbag
import rospy
import pickle

_namespace_ = 'divided_robot'
name_arm_state  = f'/{_namespace_}/trajectory_controller/state'
name_gripper_state  = f'/{_namespace_}/gripper_controller/state'
name_joint_state = f'/{_namespace_}/joint_states'

#name_cam_hand       = '/usb_cam/image_raw'
name_cam_hand       = '/Camera0/color/image_raw'

#
# determine time steps with this message
#
main_topic = name_cam_hand

use_topics = (
    name_arm_state,
    name_gripper_state,
    name_joint_state,
    name_cam_hand,
)

def twist_to_data(twist):
    ## numpy version
    return np.array((twist.linear.x, twist.linear.y, twist.angular.z), dtype='float32')
    ## list version
    #return (twist.linear.x, twist.linear.y, twist.angular.z,)

def odom_to_data(odom):
    return twist_to_data(odom.twist.twist)

### camera
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
import numpy as np
#bgr
# def _from_rosImage(msg):
#     bridge = CvBridge()
#     cv_img = bridge.imgmsg_to_cv2(msg)
#     ##
#     #return cv_img.tolist()
#     ## numpy version
#     return cv_img
def _from_rosImage(msg):
    bridge = CvBridge()
    cv_img = bridge.imgmsg_to_cv2(msg, desired_encoding='rgb8')
    ##
    #return cv_img.tolist()
    ## numpy version
    return cv_img
def find_nearest(lst, tm, start=0):
    size = len(lst)
    prev_t, prev_msg = lst[0]
    if tm <= prev_t:
        return -1, prev_t, prev_msg
    for i in range(start, size):
        t, msg = lst[i]
        if tm > prev_t and tm <= t:
            if tm - prev_t > t - tm:
                return i, t, msg
            else:
                return i - 1, prev_t, prev_msg
    return None, None, None ## last-one

convertFunctions = {
    'nav_msgs/Odometry':    odom_to_data,
    'geometry_msgs/Twist':  twist_to_data,
    'sensor_msgs/Image':    _from_rosImage,
    }

state_names = [
    "LINK_0",
    "LINK_1",
    "LINK_2",
    "LINK_3",
    "LINK_4",
    "LINK_5",
    "LINK_6",
    ]

action_names = [
    "LINK_0",
    "LINK_1",
    "LINK_2",
    "LINK_3",
    "LINK_4",
    "LINK_5",
    "LINK_6",
    ]
##
def makeStatePos(msg_joint_state):
    data = {}
    for n, p in zip(msg_joint_state.name,  msg_joint_state.position):
        data[n] = p
    res = []
    for n in state_names:
        res.append(data[n])
    return np.array(res)
def makeStateTrq(msg_joint_state):
    data = {}
    for n, p in zip(msg_joint_state.name,  msg_joint_state.effort):
        data[n] = p
    res = []
    for n in state_names:
        res.append(data[n])
    return np.array(res)
def makeAction(msg_arm_traj, msg_grip_traj):
    data = {}
    for n, p in zip(msg_arm_traj.joint_names, msg_arm_traj.desired.positions):
        data[n] = p
    for n, p in zip(msg_grip_traj.joint_names, msg_grip_traj.desired.positions):
        data[n] = p
    res = []
    for n in action_names:
        res.append(data[n])
    ## hot fix for gripper
    #idx = msg_joint_state.name.index("hand_motor_joint")
    #res.append(msg_joint_state.position[idx])
    return np.array(res)

def mainFunction(bag_file, pkl_name, rate=60.0): ## add skip or rate
    ## open bag
    bag = rosbag.Bag(bag_file)
    topic_types, topics = bag.get_type_and_topic_info()

    ## parse classes
    topic_class = {}
    for i, mname in enumerate(topic_types):
        mg = mname.split('/')
        evstr = f'from {mg[0]}.msg import {mg[1]} as msg{i:0>3}'
        print(evstr)
        exec(evstr)
        tmp = { 'class': eval(f'msg{i:0>3}') }
        if mname in convertFunctions:
            tmp['func'] = convertFunctions[mname]
        topic_class[mname] = tmp

    ## main - time
    main_msgs = []
    print(main_topic)
    useHeader = False
    if hasattr(topic_class[ topics[main_topic].msg_type ]['class'], 'header'):
        useHeader = True
    for _ , msg, t in bag.read_messages(topics=[main_topic]):
        print('.', end='', flush=True)
        if useHeader:
            tm = rospy.Time(secs=msg.header.stamp.secs, nsecs=msg.header.stamp.nsecs).to_sec()
        else:
            tm = t.to_sec()
        main_msgs.append( (tm, tm,) )
    print('!')

    ## store all messages
    all_msgs = {}
    for tname in use_topics:
        if not tname in topics:
            continue
        useHeader = False
        if hasattr(topic_class[ topics[tname].msg_type ]['class'], 'header'):
            useHeader = True
        ##
        lst = []
        # func = topic_class[ topics[tname].msg_type ]['func'] if 'func' in  topic_class[ topics[tname].msg_type ] else None
        # print(tname, func)
        for _ , msg, t in bag.read_messages(topics=[tname]):
            print('.', end='', flush=True)
            if useHeader:
                tm = rospy.Time(secs=msg.header.stamp.secs, nsecs=msg.header.stamp.nsecs).to_sec()
            else:
                tm = t.to_sec()
            #if func is not None:
            #    msg = func(msg)
            lst.append( (tm, msg,) )
        print('!')
        all_msgs[tname] = lst

    ## find nearest messages based on time
    final_msgs = {}
    for tname in use_topics:
        if not tname in all_msgs:
            continue
        lst = all_msgs[tname]
        idx = 0
        res = []
        print(tname)
        for tm, _ in main_msgs:
            idx, t, msg = find_nearest(lst, tm, start = idx)
            res.append( (t, msg, idx, ) )
            if idx is None:
                idx = len(lst)-1
            if idx < 0:
                idx = 0
        final_msgs[tname] = res 
    final_msgs['T'] = main_msgs
    #final_msgs['__topic_types'] = topic_types
    #final_msgs['__topics'] = topics

    ### remove None
    doing = True
    while doing:
        remove_idx = -1
        for key, lst in final_msgs.items():
            for idx, l in enumerate(lst):
                if l[0] is None:
                    remove_idx = idx
                    break
            if remove_idx >=0:
                break
        if remove_idx >=0:
            ## remove remove_idx
            print('remove : ', idx)
            for key, lst in final_msgs.items():
                del lst[remove_idx]
        else:
            ## all data is not None
            doing = False

    ### TODO: skip or rate
    if rate is not None:
        dur = 1 / rate
        indices = [0]
        tm = final_msgs['T']
        prev = tm[0][0]
        for idx in range(len(tm)):
            cur = tm[idx][0]
            if cur - prev >= dur:
                indices.append(idx)
                prev = cur
        tmp = final_msgs
        final_msgs = {}
        for k in tmp.keys():
            res = []
            vals = tmp[k]
            for idx in indices:
                res.append(vals[idx])
            final_msgs[k] = res

    ### convert msgs -> np.array
    arrays = {}
    sz = len(final_msgs['T'])
    print(sz)
    arrays['state_pos']   = []
    arrays['state_trq']   = []
    arrays['action_pos']  = []
    arrays['hand_image']  = []
    arrays['reward']=[]
    arrays['T'] = []
    for idx in range(sz):
        state_pos = makeStatePos(
            final_msgs[name_joint_state][idx][1],
        )
        state_trq = makeStateTrq(
            final_msgs[name_joint_state][idx][1],
        )
        action = makeAction(
            final_msgs[name_arm_state][idx][1],
            final_msgs[name_gripper_state][idx][1],
        )
        hand_image = _from_rosImage( final_msgs[name_cam_hand][idx][1] )
        arrays['state_pos' ].append(state_pos)
        arrays['state_trq' ].append(state_trq)
        arrays['action_pos'].append(action)
        arrays['hand_image'].append(hand_image)
        arrays['reward'].append(0.0)
        arrays['T'].append(final_msgs['T'][idx][0])
    with open(pkl_name, 'wb') as f:
        pickle.dump(arrays, f)

    return arrays
