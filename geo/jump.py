import pygame

JUMP_VELOCITY = -15.0


def manage_jump(event, is_grounded):
    return (
        is_grounded
        and event.type == pygame.KEYDOWN
        and event.key == pygame.K_SPACE
    )