import pygame
from pygame.locals import *
from app import App 
from assets import ASSET_DICT
from controls.keyboard import Keyboard


class ControllerViewer(App):
    """
    displays all the assets one at a time.
    use left and right arrow keys to seek through them.
    """
    def __init__(self, ctlr):
        super(ControllerViewer, self).__init__("Controller Viewer")

        self.bg = ASSET_DICT['gamepad']
        self.ctlr = ctlr

    def handle_event(self, event):
        self.quit_if_needed(event)

    def render(self):
        super(ControllerViewer, self).render()
        self.screen.blit(self.bg, self.offset)

        for button in self.ctlr.BUTTON_METHOD_NAMES:
            if self.ctlr.invoke(button):
                self.screen.blit(ASSET_DICT[button], self.offset)


if __name__ == '__main__':
    ControllerViewer(Keyboard()).main()
