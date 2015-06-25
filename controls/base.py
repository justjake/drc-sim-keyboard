from __future__ import print_function
from functools import partial
from util import log
"""
Abstract keybindings for drc-sim
"""
TINY_BUT_NON_ZERO_NUMBER = 0.0000001
BUTTONS = {
    'SYNC': 0x0001,
    'HOME': 0x0002,
    'MINUS': 0x0004,
    'PLUS': 0x0008,
    'R': 0x0010,
    'L': 0x0020,
    'ZR': 0x0040,
    'ZL': 0x0080,
    'DOWN': 0x0100,
    'UP': 0x0200,
    'RIGHT': 0x0400,
    'LEFT': 0x0800,
    'Y': 0x1000,
    'X': 0x2000,
    'B': 0x4000,
    'A': 0x8000
}

EXTRA_BUTTONS = {
    'R3': 0x40,
    'L3': 0x80,
}


def inspect_mask(integer, bits=8, byte=8):
    """
    print a value as a bits. printing in byte-sized blocks

    >>> bits(255)
    '11111111'

    >>> bits(256)
    '00000001 00000000'
    """
    as_bin = bin(integer)[2:]
    if len(as_bin) < bits:
        missing_bits = bits - len(as_bin)
        as_bin = '0' * missing_bits + as_bin

    return ' '.join(chunks(as_bin, byte))


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


def button_mask(controls):
    """
    Given controls, a `Controls` instance, compute the bitmask of all pressed
    buttons. Returns an int.
    """
    mask = 0
    for button_name, button_mask in BUTTONS.iteritems():
        if controls.invoke(button_name.lower()):
            mask |= button_mask
    return mask


def extra_button_mask(controls):
    mask = 0
    for button_name, button_mask in EXTRA_BUTTONS.iteritems():
        if controls.invoke(button_name.lower()):
            mask |= button_mask
            #log('wow special button {b} clicked and invoked! new mask {m}'.format(
                #b=button_name, m=mask), 'FUGGIN BUTTANS')
    return mask


class Controls(object):
    """
    base class for implementing Wii U control schemes.
    """

    BUTTON_METHOD_NAMES = map(lambda x: x.lower(), BUTTONS.keys()) + [
        'l3',
        'r3',
        'tv',  # most useless of buttans
    ]

    def invoke(self, name):
        return getattr(self, name)()

    """
    buttons. should return True if pressed.
    """
    # face buttons
    def a(self):
        return False

    def b(self):
        return False

    def x(self):
        return False

    def y(self):
        return False

    # triggers
    def r(self):
        return False

    def l(self):
        return False

    def zr(self):
        return False

    def zl(self):
        return False

    # dpad
    def down(self):
        return False

    def up(self):
        return False

    def right(self):
        return False

    def left(self):
        return False

    # start buttons
    def home(self):
        return False

    def minus(self):
        return False

    def plus(self):
        return False

    # joystick presses
    def r3(self):
        return False

    def l3(self):
        return False

    # extra bullshit. Unsure of utility of implementing these
    def sync(self):
        return False

    def tv(self):
        return False

    """
    Sticks. Should return an (x :: number, y :: number) tuple. 
    
    x and y should be in (-1, 1).
    clicked should be true when the stick is pushed in (L3 or R3 in PS3)
    """
    def left_stick(self):
        return (0, 0)

    def right_stick(self):
        return (0, 0)

    """
    should return a tuple (x, y, z) of acceleration, in (-1, 1).
    """
    def accelerometer(self):
        return (0, 0, 0)

    """
    should return a tuple (roll, yaw, pitch) of values in 
    """
    def gyroscope(self):
        return (0, 0, 0)

    """
    should return a tuple (x, y, force) of a touch location.
    force should be a float between 0 and 1.

    return None if there is no touch.
    """
    def touch(self):
        return None

    def handle_event(self, event):
        """
        override if you wish to handle events with your controller
        """ pass




class MethodMissing(object):
    def method_missing(self, name, *args, **kwargs):
        '''please implement'''
        raise NotImplementedError('please implement a "method_missing" method')

    def __getattr__(self, name):
        if name == 'BUTTON_METHOD_NAMES':
            return Controls.BUTTON_METHOD_NAMES
        return partial(self.method_missing, name)


class UnionController(MethodMissing):
    def __init__(self, controllers):
        self.controllers = controllers

    def method_missing(self, name, *args, **kwargs):
        if name == 'invoke':
            return self.method_missing(args[0], *args[0:])

        if name in ('left_stick', 'right_stick'):
            total = (0, 0)
            for ctlr in self.controllers:
                total = add(total, ctlr.invoke(name))
            return total

        if name in self.controllers[0].BUTTON_METHOD_NAMES:
            total = False
            for ctlr in self.controllers:
                total = total or ctlr.invoke(name)
            return total

        for ctlr in self.controllers:
            getattr(ctlr, name)(*args, **kwargs)


def build_response(controls):
    pass


def scale(OldValue, OldMin, OldMax, NewMin, NewMax):
    divisor = OldMax - OldMin
    if divisor == 0:
        divisor = TINY_BUT_NON_ZERO_NUMBER  # a tiny but non-zero number
        log('avoided division by zero through trickery', 'base-scale')
    return (((OldValue - OldMin) * (NewMax - NewMin)) /
            (divisor) + NewMin)


def add(point_a, point_b):
    return (point_a[0] + point_b[0], point_a[1] + point_b[1])


def wiiu_axis(orig):
    """
    given a joystick axis motion, scale into Wii U space
    """
    if abs(orig) < 0.0001:
        # unsure why this starts as this value 0x800
        return 0x800
    return int(scale(orig, -1, 1, 900, 3200))

###
# TODO: move control value constructors to new file
###
