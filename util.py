from __future__ import print_function
import sys
 

def log(msg, name='DRK'):
    print(' [ {name} ] -> {msg}'.format(name=name, msg=msg),
          file=sys.stderr)

GAMEPAD_DIM = (854, 480)
