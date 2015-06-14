from base import Controls
import pygame
from pygame.locals import *


class Keyboard(Controls):
    """
    not much heart going into this one since KeyboardMouse needs more love

    gonna use it as a proof-of-controler_viewer.py
    """
    def key(self, name):
        return pygame.key.get_pressed()[name]

    # face buttons
    def a(self):
        return self.key(K_h)

    def b(self):
        return self.key(K_j)

    def x(self):
        return self.key(K_k)

    def y(self):
        return self.key(K_l)

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
