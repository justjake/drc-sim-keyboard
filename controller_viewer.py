import pygame
from pygame.locals import *
from app import App 
from assets import ASSET_DICT
from controls.keyboard import Keyboard
from controls.base import scale


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def scale_stick(old_value, new_min, new_max):
    return scale(old_value, -1, 1, new_min, new_max)


class StickField(object):
    def __init__(self, center):
        self.center = center
        self.width = 164
        self.height = 164
        self.point_width = 20
        self.point_height = 20

        self.point = ASSET_DICT['point']
        self.field = ASSET_DICT['stick-field']

    def _top_left(self):
        x, y = self.center
        return (x - self.width / 2, y - self.height / 2)

    def _point_top_left(self, joystick_axes):
        x, y = joystick_axes
        xoff = scale_stick(x, 164/2, -164/2)
        yoff = scale_stick(y, -164/2, 164/2)
        center_x, center_y = self.center
        point = (center_x - xoff - self.point_width / 2, center_y - yoff - self.point_height / 2)
        return point

    def render_to(self, target, joystick_axes):
        target.blit(self.field, self._top_left())
        target.blit(self.point, self._point_top_left(joystick_axes))


class ControllerViewer(App):
    """
    displays all the assets one at a time.
    use left and right arrow keys to seek through them.
    """
    def __init__(self, ctlr):
        super(ControllerViewer, self).__init__("Controller Viewer")

        self.bg = ASSET_DICT['gamepad']
        self.ctlr = ctlr
        self.left_vis = StickField(add((265, 280), self.offset))
        self.right_vis = StickField(add((1405, 280), self.offset))

    def handle_event(self, event):
        self.quit_if_needed(event)

    def render(self):
        super(ControllerViewer, self).render()
        self.screen.blit(self.bg, self.offset)

        for button in self.ctlr.BUTTON_METHOD_NAMES:
            if self.ctlr.invoke(button):
                self.screen.blit(ASSET_DICT[button], self.offset)

        self.left_vis.render_to(self.screen, self.ctlr.left_stick())
        self.right_vis.render_to(self.screen, self.ctlr.right_stick())
        # print('left_stick', self.ctlr.left_stick())
        # print('right_stick', self.ctlr.right_stick())

if __name__ == '__main__':
    ControllerViewer(Keyboard()).main()
