import pygame
from assets import ASSET_DICT, load_all_assets


class ExitMain(StandardError):
    """
    signals that we want to exit the main loop of the app
    """
    pass


class App(object):
    """
    takes care of a lot of the boring bits of our standard app, like loading
    the assets and sizing up the screen.
    """
    def __init__(self, title):
        pygame.init()
        pygame.display.set_caption(title)
        pygame.display.set_mode((20, 20))
        load_all_assets()
        asset_names = ASSET_DICT.keys()

        # set screen size to always fit the assets
        BORDER_W = 10
        BORDER_H = 10
        max_w = 0
        max_h = 0
        for name in asset_names:
            asset = ASSET_DICT[name]
            w = asset.get_width()
            h = asset.get_height()
            if h > max_h:
                max_h = h
            if w > max_w:
                max_w = w
        screen = pygame.display.set_mode(
            (BORDER_W + max_w + BORDER_W,
             BORDER_H + max_h + BORDER_H)
        )

        print("width", screen.get_width())
        print("height", screen.get_height())

        self.screen = screen
        self.offset = (BORDER_W, BORDER_H)
        return self.screen, self.offset

    def handle_event(self, event):
        """
        called on each event in the main loop
        """
        pass

    def quit_if_needed(self, event):
        if (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            raise ExitMain('escape')

        elif (event.type == pygame.QUIT):
            raise ExitMain('quit event')

    def handle_all_events(self):
        events = pygame.event.get()
        for event in events:
            self.handle_event(event)

    def render(self):
        """
        run each frame.
        """
        self.screen.fill(0)

    def main(self):
        while True:
            try:
                self.handle_all_events()
                self.render()
                pygame.display.flip()
            except ExitMain:
                break
        pygame.display.quit()
