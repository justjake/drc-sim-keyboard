import pygame
from pygame.locals import *
from base import add, scale
from keyboard import Keyboard


class MouseJoystick(object):
    def __init__(self):
        # always added to the "max" movement
        self.sensitivity = 0
        self.sensitivity_incr = 10
        self.max = 100.0
        # this is really weird. blame VirtualBox?
        self.max_locked = 25000.0

    def handle_event(self, event):
        """
        call during your event loop to enable ajusting sensitivity and stuff
        """
        if event.type == KEYDOWN:
            is_locked = pygame.event.get_grab()

            if event.key == K_CAPSLOCK:
                if is_locked:
                    self.unlock()
                else:
                    self.lock()

            if is_locked:
                if event.key == K_LEFT:
                    self.sensitivity -= self.sensitivity_incr

                if event.key == K_RIGHT:
                    self.sensitivity += self.sensitivity_incr

    def get(self):
        """
        gets the joystick pairs
        """
        dx, dy = pygame.mouse.get_rel()
        if (dx + 0.1) * (dy * 0.5) > 2:
            print("pygame mouse movement", dx, dy)

        maximum = self.max
        if pygame.event.get_grab():
            maximum = self.max_locked

        x = scale(float(dx), 
                  -(maximum + self.sensitivity),
                  maximum + self.sensitivity, 
                  -1.0, 1.0)
        y = scale(float(dy),
                  -(maximum + self.sensitivity),
                  maximum + self.sensitivity, 
                  1.0, -1.0)
        return (x, y)

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
