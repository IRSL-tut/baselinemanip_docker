import pyspacemouse

#
# require settings
# pip install pyspacemouse
#

def callback_button(state, buttons):
    print("bc: ", state, buttons)

def callback_dof(*arg, **kwargs):
    print("dof: ", arg, kwargs)

sm = pyspacemouse.open(button_callback=callback_button, dof_callback=callback_dof)

sm.read()
