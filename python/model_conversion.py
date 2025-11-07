##
## directory mujoco_scanned_objects.git ?
## RoboManipBaselines/robo_manip_baselines/envs/assets/mujoco/mujoco_scanned_objects
## https://github.com/kevinzakka/mujoco_scanned_objects
##
exec(open('/choreonoid_ws/install/share/irsl_choreonoid/sample/irsl_import.py').read())
import os

names = [ '45oz_RAMEKIN_ASST_DEEP_COLORS',
'ACE_Coffee_Mug_Kristen_16_oz_cup',
'Beta_Glucan',
'Curver_Storage_Bin_Black_Small',
'Sapota_Threshold_4_Ceramic_Round_Planter_Red',
'Shurtape_Tape_Purple_CP28',
'Target_Basket_Medium',
'Threshold_Porcelain_Spoon_Rest_White',
'Twinlab_Nitric_Fuel',
'Wishbone_Pencil_Case',
'Womens_Suede_Bahama_in_Graphite_Suede_cUAjIMhWSO9', ]

## making names by os.listdir(src_dir)

def make_model(name, src_dir='mujoco_scanned_objects', dest_dir='/tmp'):
    ## TODO : checking src_dir/dest_dir
    os.chdir(f'{src_dir}/{name}')
    rb=RobotBuilder()
    obj=rb.loadMesh( 'model.obj' )
    obj.object.getChild(0).getChild(0).setTextureImage( 'texture.png' )
    root=rb.createLinkFromShape(name='Root', root=True, density=1600.0)
    mkshapes.removeCollisionInLink(rb.body.rootLink)
    for i in range(32): ## fixed size of collision meshes
        obj=rb.loadMesh(f'model_collision_{i}.obj', rawShape=True)
        rb.body.rootLink.addCollisionShapeNode(obj)
    rb.exportBody(f'{dest_dir}/{name}.body', modelName=name)
    os.chdir('../..')
