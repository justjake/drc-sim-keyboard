import pygame
from pygame.locals import *
from os import path
from Controls import BUTTONS

ASSET_ROOT = path.join(path.dirname(path.abspath(__file__)), 'assets')
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
        'gamepad'
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
    pygame.init()
    pygame.display.set_caption('Asset Viewer')
    pygame.display.set_mode((1000, 1000))
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

    font = pygame.font.SysFont("Courier", 40)

    # main loop
    current_asset = 0

    while True:
        events = pygame.event.get()
        screen.fill(0)

        for event in events:
            if (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.display.quit()
                return

            elif (event.type == QUIT):
                pygame.display.quit()
                return

            if (event.type == KEYDOWN and event.key == K_LEFT):
                current_asset = (current_asset - 1) % len(asset_names)

            if (event.type == KEYDOWN and event.key == K_RIGHT):
                current_asset = (current_asset + 1) % len(asset_names)

        asset = ASSET_DICT[asset_names[current_asset]]
        screen.blit(asset, (BORDER_W, BORDER_H))
        screen.blit(
            font.render(
                asset_names[current_asset],
                True,
                (255, 255, 255),
                (0, 0, 0)),
            (BORDER_W, BORDER_H)
        )

        pygame.display.flip()

if __name__ == '__main__':
    asset_viewer()
