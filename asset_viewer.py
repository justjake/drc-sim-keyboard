import pygame
from pygame.locals import *
from app import App 
from asset_manager import ASSET_DICT


class AssetViewer(App):
    """
    displays all the assets one at a time.
    use left and right arrow keys to seek through them.
    """
    def __init__(self):
        super(AssetViewer, self).__init__("Asset Viewer")

        self.font = pygame.font.SysFont("Courier", 40)
        self.current_asset = 0
        self.asset_names = ASSET_DICT.keys()

    def handle_event(self, event):
        self.quit_if_needed(event)
        if (event.type == KEYDOWN and event.key == K_LEFT):
            self.current_asset = (self.current_asset - 1) % len(self.asset_names)

        if (event.type == KEYDOWN and event.key == K_RIGHT):
            self.current_asset = (self.current_asset + 1) % len(self.asset_names)

    def render(self):
        super(AssetViewer, self).render()

        asset = ASSET_DICT[self.asset_names[self.current_asset]]
        self.screen.blit(asset, self.offset)
        self.screen.blit(
            self.font.render(
                self.asset_names[self.current_asset],
                True,
                (255, 255, 255),
                (0, 0, 0)),
            self.offset
        )

if __name__ == '__main__':
    AssetViewer().main()
