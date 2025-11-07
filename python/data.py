
### Reading RmbData
from robo_manip_baselines.common import RmbData, DataKey

with RmbData(rmb_file_path) as rmb_data:
    data_shape  = rmb_data[DataKey.MEASURED_JOINT_POS].shape
    single_data = rmb_data[DataKey.MEASURED_JOINT_POS][0]
    sliced_data = rmb_data[DataKey.MEASURED_JOINT_POS][1:4]
    whole_data  = rmb_data[DataKey.MEASURED_JOINT_POS][:]

    camera_name = "front"
    single_rgb = rmb_data[DataKey.get_rgb_image_key(camera_name)][1]
    sliced_depth = rmb_data[DataKey.get_depth_image_key(camera_name)][::10]

### Making RmbData

from robo_manip_baselines.common import RmbData, DataKey
from robo_manip_baselines.common.manager.DataManager import DataManager

def make_new_data(rmb_data, dest, demo_name='demo0', task_name='task0'):
    data_manager=DataManager(None, demo_name, task_name)
    #
    length = rmb_data[DataKey.TIME].shape[0]
    for i in range(length):
        print(i)
        data_manager.append_single_data(DataKey.TIME, rmb_data[DataKey.TIME][i])
        data_manager.append_single_data(DataKey.REWARD, rmb_data[DataKey.REWARD][i])
        ##
        for key in (DataKey.MEASURED_JOINT_POS, ):
            measured_data = rmb_data[key][i]
            data_manager.append_single_data(key, measured_data)
        ##
        for key in (DataKey.COMMAND_JOINT_POS, ):
            command_data = rmb_data[key][i]
            data_manager.append_single_data(key, command_data)
        ##
        #for camera_name in ('hand', ):
        #    ##
        #    img_key = DataKey.get_rgb_image_key(camera_name)
        #    img = rmb_data[img_key][i]
        #    data_manager.append_single_data(img_key, img)
        #    ##
        #    dpt_key = DataKey.get_depth_image_key(camera_name)
        #    dpt = rmb_data[dpt_key][i]
        #    data_manager.append_single_data(dpt_key, dpt)
    #destination
    data_manager.save_data(dest)

# convert original .rmb => new .rmb
for nm in os.listdir('temp/dataset00'):
    fn = 'temp/dataset00/' + nm
    print(fn)
    with RmbData(fn) as rmb_data:
        dn = 'temp/new00/' + nm
        make_new_data(rmb_data, dn)

##
#
#FLS=$(cd dataset00; ls -1)
#for f in $FLS; do
#  cp dataset00/$f/hand_rgb_image.rmb.mp4 new00/$f/hand_rgb_image.rmb.mp4
#  cp dataset00/$f/hand_rgb_depth.rmb.mp4 new00/$f/hand_rgb_depth.rmb.mp4
#done
