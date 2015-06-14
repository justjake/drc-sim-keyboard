#!/usr/bin/env python
# renames to nice filenames from the bullshit that Photoshop's 
# File -> Scripts -> Layers to Files uses
import os

here = os.path.dirname(os.path.abspath(__file__))
for filename in os.listdir(here):
    if filename.startswith('gamepad_') and filename.endswith('.png'):
        old_name, _ = os.path.splitext(filename)
        old_name = old_name.split("_")
        new_name = old_name[0] + "-" + old_name[2] + '.png'
        print("{} --> {}".format(filename, new_name))
        os.rename(os.path.join(here, filename), os.path.join(here, new_name))
