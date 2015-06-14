from base import Controls

class Xbox360Wireless(Controls):
    """
    Bindings to map the standard buttons on a 360 controller to the Wii U
    gamepad.

    Pass in a pygame joystick object to get the party started.

    --! UNTESTED !--
    """
    def __init__(self, joystick):
        self.joy = joystick

    """
    buttons. should return True if pressed.
    """
    def sync(self):
        return False

    def home(self):
        return self.joy.get_button(8)

    def minus(self):
        return self.joy.get_button(6)

    def plus(self):
        return self.joy.get_button(7)

    # triggers
    def r(self):
        return self.joy.get_button(5)

    def l(self):
        return self.joy.get_button(4)

    def zr(self):
        # the 360's analog triggers are represented as axies.
        # we actuate if they're squeezed at all.
        return self.joy.get_axis(5) > 0

    def zl(self):
        return self.joy.get_axis(2) > 0

    # dpad
    def down(self):
        return self.joy.get_button(14)

    def up(self):
        return self.joy.get_button(13)

    def right(self):
        return self.joy.get_button(12)

    def left(self):
        return self.joy.get_button(11)

    # face buttons
    def y(self):
        return self.joy.get_button(3)

    def x(self):
        return self.joy.get_button(2)

    def b(self):
        return self.joy.get_button(1)

    def a(self):
        return self.joy.get_button(0)

    # extra buttons - joystick presses
    def r3(self):
        return False

    def l3(self):
        return False

    # the 'TV' button. Unsure of utility of implementing this.
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


class ProMap360(Xbox360Wireless):
    """
    subclass of Xbox360Wireless where a & b and x & y are swapped, so it feels
    like the Wii U Pro Controller button layout.
    """
    def a(self):
        return super(ProMap360, self).b()

    def b(self):
        return super(ProMap360, self).a()

    def x(self):
        return super(ProMap360, self).y()

    def y(self):
        return super(ProMap360, self).x()
