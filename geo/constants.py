from pathlib import Path

import pygame

WIDTH, HEIGHT = 800, 600

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

ASSET_DIR = Path(__file__).resolve().parent.parent


def load_ground(level):
    ground_files = {
        1:"groundl1.png",
        2: "groundl2.png",
        3: "groundl3.jpg",
        4: "groundl4.jpg",
    }
    image_path = ASSET_DIR / ground_files[min(level, 4)]
    image = pygame.image.load(str(image_path))
    if level == 3:
        ground_top = 775
        return image.subsurface(
            pygame.Rect(0, ground_top, 800, image.get_height() - ground_top)
        ).copy()
    if level >= 4:
        return image
    return image.subsurface(pygame.Rect(30, 0, 800, image.get_height())).copy()


GROUND = load_ground(1)

player_image = pygame.image.load(str(ASSET_DIR / "player.png")).convert_alpha()
player1j = pygame.image.load(str(ASSET_DIR / "player1j.png")).convert_alpha()


