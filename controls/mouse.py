import pygame
from pygame.locals import *
from base import add, scale
from keyboard import Keyboard
from util import log  # TODO switch to absolute paths


JOYSTICK_MIN = 0.2
TOGGLE_LOCK_KEY = K_BACKQUOTE
# lag high-magnitude movements another frame
ENABLE_LAG = True
ENABLE_DOUBLE_LAG = True
MAX_MOVEMENT = 50.0


def lag(final, prev):
    """
    returns final_value, new_value_of_prev
    """
    # TO DO: do first divivative and check the subtraction of one vector
    # from another to make sure they're going the same direction?

    # TO DO: switch joystick magnitude measuring to polar-coordiate vectors
    # and mreasure magnitude of both axes at once
    if ENABLE_LAG and abs(prev) > 0.8 > abs(final):
            # swap em. we'll play this frame again to smooth the falloff
            # and we get a bonus frame of high-magnitude movement
            log('lagged {prev} again instead of {final}'.format(prev=prev, final=final), 'MOUSE')
            if ENABLE_DOUBLE_LAG:
                diff = prev - final
                return (prev, 0.6 * diff + final)
            return (prev, final)
    return (final, final)


class MouseJoystick(object):
    def __init__(self):
        # always added to the "max" movement
        self.sensitivity = 0
        self.sensitivity_incr = 10
        self.max = MAX_MOVEMENT
        # this is really weird. blame VirtualBox?
        # self.max_locked = 25000.0

        # set to the more reasonable 100.0 because most people aren't running
        # their simulator in VirtualBox
        self.max_locked = self.max
        self._prev_x = 0.0
        self._prev_y = 0.0
        log('remember to disable mouse acceleration in your desktop',
            'MOUSE')

    # core interface up front
    def get(self):
        """
        gets the joystick pairs
        """
        dx, dy = pygame.mouse.get_rel()
        #if abs(dx) > 0 or abs(dy) > 0:
            #log("pygame mouse movement: ({dx}, {dy})".format(dx=dx, dy=dy),
                #'MOUSE')

        return (self.convert_x_axis(dx), self.convert_y_axis(dy))

    def convert_x_axis(self, dx):
        final, self._prev_x = lag(self.convert_axis(dx), self._prev_x)
        return final

    def convert_y_axis(self, dy):
        final, self._prev_y = lag(self.convert_axis(dy) * -1, self._prev_y)
        return final

    def get_max(self):
        maximum = self.max + self.sensitivity
        if pygame.event.get_grab():
            maximum = self.max_locked + self.sensitivity
        return max(maximum, 1)

    def convert_axis(self, d):
        """
        convert a mouse delta into a joystick axis magnitude in (-1, 1)
        """
        # base case: no movement
        if d == 0:
            return 0

        magnitude = abs(d)
        direction = d/magnitude

        # linear conversion.

        scaled = scale(
            float(abs(d)),                       # value
            0.0,                                 # old min
            float(self.get_max()),               # old max
            max(JOYSTICK_MIN, 0.0),              # new min -- escape deadzone
            1.0                                  # new max
        )

        # ensure withing acceptable bounds
        scaled = max(min(1.0, scaled), 0.0)

        # re-apply the sign
        final = scaled * direction


        return final

    def handle_event(self, event):
        """
        call during your event loop to enable ajusting sensitivity and stuff
        and locking the mosue etc etc
        """
        if event.type == KEYDOWN:
            is_locked = pygame.event.get_grab()

            if event.key == TOGGLE_LOCK_KEY:
                if is_locked:
                    self.unlock()
                else:
                    self.lock()

            if is_locked:
                if event.key == K_COMMA:
                    self.sensitivity -= self.sensitivity_incr
                    log('[-] set sensitivity to {s}, delta_max is {max} (lower = more sensitive)'.format(s=self.sensitivity, max=self.get_max()), 'MOUSE')

                if event.key == K_PERIOD:
                    self.sensitivity += self.sensitivity_incr
                    log('[+] set sensitivity to {s}, delta_max is {max} (lower = more sensitive)'.format(s=self.sensitivity, max=self.get_max()), 'MOUSE')

    def is_locked(self):
        return pygame.event.get_grab()

    def lock(self):
        """
        locks the mouse to the window, enabling accurate readings
        """
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)

    def unlock(self):
        """
        unlocks the mouse, allowing you to mouse around for fun
        """
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)


class KeyboardMouse(Keyboard):
    def __init__(self):
        super(KeyboardMouse, self).__init__()
        self.mouse = MouseJoystick()

    def right_stick(self):
        return self.mouse.get()

    def handle_event(self, event):
        """
        handle events here so the mouse can adjust sensitivity
        """
        self.mouse.handle_event(event)

    def r(self):
        if self.mouse.is_locked():
            return pygame.mouse.get_pressed()[2]

    def zr(self):
        if self.mouse.is_locked():
            return pygame.mouse.get_pressed()[0]

    def r3(self):
        if self.mouse.is_locked():
            return pygame.mouse.get_pressed()[1]
