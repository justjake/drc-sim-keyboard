import pygame
from pygame.locals import *
from base import add, scale
from keyboard import Keyboard


TOGGLE_LOCK_KEY = K_BACKQUOTE


class MouseJoystick(object):
    def __init__(self):
        # always added to the "max" movement
        self.sensitivity = 0
        self.sensitivity_incr = 10
        self.max = 60.0
        # this is really weird. blame VirtualBox?
        # self.max_locked = 25000.0
        
        # set to the more reasonable 100.0 because most people aren't running
        # their simulator in VirtualBox
        self.max_locked = self.max

    # core interface up front
    def get(self):
        """
        gets the joystick pairs
        """
        dx, dy = pygame.mouse.get_rel()
        if abs(dx) > 0 or abs(dy) > 0:
            print("pygame mouse movement", dx, dy)

        return (self.convert_x_axis(dx), self.convert_y_axis(dy))

    def convert_x_axis(self, dx):
        return self.convert_axis(dx)

    def convert_y_axis(self, dy):
        return self.convert_axis(dy) * -1

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
        maximum = self.max
        if pygame.event.get_grab():
            maximum = self.max_locked

        scaled = scale(
            float(abs(d)),                       # value
            0.0,                                 # old min
            float(maximum + self.sensitivity),   # old max
            0.1,                                 # new min -- escape deadzone
            1.0                                  # new max
        )

        # ensure withing acceptable bounds
        scaled = max(min(1.0, scaled), 0.0)

        # re-apply the sign
        return scaled * direction

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
                if event.key == K_LEFT:
                    self.sensitivity -= self.sensitivity_incr

                if event.key == K_RIGHT:
                    self.sensitivity += self.sensitivity_incr

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
        return pygame.mouse.get_pressed()[2]

    def zr(self):
        return pygame.mouse.get_pressed()[0]

    def r3(self):
        return pygame.mouse.get_pressed()[1]
