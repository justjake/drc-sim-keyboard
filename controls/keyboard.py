from base import Controls, add
import pygame
from pygame.locals import *


def make_joy_emu(mapping):
    def get():
        pos = (0, 0)
        pressed = pygame.key.get_pressed()
        for key, vector in mapping.iteritems():
            if pressed[key]:
                pos = add(pos, vector)
        return pos
    return get


class Keyboard(Controls):
    """
    not much heart going into this one since KeyboardMouse needs more love

    gonna use it as a proof-of-controler_viewer.py
    """
    def key(self, name):
        return pygame.key.get_pressed()[name]

    def __init__(self):
        self.lstick = make_joy_emu({
            K_w: (0, 1),
            K_s: (0, -1),
            K_a: (-1, 0),
            K_d: (1, 0),
        })

        self.rstick = make_joy_emu({
            K_UP: (0, 1),
            K_DOWN: (0, -1),
            K_LEFT: (-1, 0),
            K_RIGHT: (1, 0),
        })

    # face buttons
    def a(self):
        return self.key(K_h) or self.key(K_RETURN)

    def b(self):
        return self.key(K_j) or self.key(K_BACKSPACE)

    def x(self):
        return self.key(K_k) or self.key(K_SPACE)

    def y(self):
        return self.key(K_l) or self.key(K_q)

    # triggers
    def r(self):
        return False

    def l(self):
        return False

    def zr(self):
        return False

    def zl(self):
        return (pygame.key.get_mods() & KMOD_LCTRL or
                pygame.key.get_mods() & KMOD_LSHIFT)

    # dpad
    def down(self):
        return self.key(K_DOWN)

    def up(self):
        return self.key(K_UP)

    def right(self):
        return self.key(K_RIGHT)

    def left(self):
        return self.key(K_LEFT)

    # start buttons
    def home(self):
        return False

    def minus(self):
        return self.key(K_MINUS)

    def plus(self):
        return self.key(K_EQUALS)

    # joystick presses
    def r3(self):
        return self.key(K_e)

    def l3(self):
        return False

    def left_stick(self):
        return self.lstick()

    def right_stick(self):
        return self.rstick()
