import pygame
from pygame.locals import *
from os import path
from controls.base import BUTTONS

ASSET_ROOT = path.join(path.dirname(path.abspath(__file__)), 'asset_files')
ASSET_DICT = {}


def asset_path(relative_filename):
    return path.join(ASSET_ROOT, relative_filename)


def load_png(full_path):
    """
    load a PNG into a surface
    """
    return pygame.image.load(full_path).convert_alpha()


def load_all_assets():
    """
    loads all the assets into ASSET_DICT as screen-ready surfaces

    TODO: make ASSET_DICT a struct for faster lookups?
    """
    buttons = map(lambda x: x.lower(), BUTTONS.keys())
    other_gamepad_images = [
        'screen-x409-y247',
        'l3',
        'r3',
        'gamepad',
        'stick-field',
        'point'
    ]
    gamepad_asset_names = buttons + other_gamepad_images
    gamepad_asset_files = map(
        lambda n: asset_path('gamepad-' + n + '.png'),
        buttons + other_gamepad_images)
    for i in xrange(len(gamepad_asset_files)):
        ASSET_DICT[gamepad_asset_names[i]] = load_png(gamepad_asset_files[i])


def asset_viewer():
    """
    this is for testing image loading.
    draws all assets to the screen in whatever order we get.
    """
    screen, offset = set_up('Asset Viewer')
    font = pygame.font.SysFont("Courier", 40)

    # main loop
    asset_names = ASSET_DICT.keys()
    current_asset = 0

    while True:
        events = pygame.event.get()
        screen.fill(0)

        for event in events:

            if (event.type == KEYDOWN and event.key == K_LEFT):
                current_asset = (current_asset - 1) % len(asset_names)

            if (event.type == KEYDOWN and event.key == K_RIGHT):
                current_asset = (current_asset + 1) % len(asset_names)

        asset = ASSET_DICT[asset_names[current_asset]]
        screen.blit(asset, offset)
        screen.blit(
            font.render(
                asset_names[current_asset],
                True,
                (255, 255, 255),
                (0, 0, 0)),
            offset
        )

        pygame.display.flip()

if __name__ == '__main__':
    asset_viewer()
