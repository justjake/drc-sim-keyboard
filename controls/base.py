"""
Abstract keybindings for drc-sim
"""
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

EXTRA_BOTTOMS = {
    'L3': 0x08,
    'R3': 0x04,
}


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
    for button_name, button_mask in EXTRA_BOTTOMS.iteritems():
        if controls.invoke(button_name.lower()):
            mask |= button_mask
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


def build_response(controls):
    pass


def scale(OldValue, OldMin, OldMax, NewMin, NewMax):
    return int((
        ((OldValue - OldMin) * (NewMax - NewMin)) /
        (OldMax - OldMin)) + NewMin)


def add(point_a, point_b):
    return (point_a[0] + point_b[0], point_a[1] + point_b[1])
