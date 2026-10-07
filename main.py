import random
import sys
import time
from pathlib import Path

import pygame

pygame.init()
pygame.display.set_mode((800, 600))

from geo.constants import GROUND, WHITE, player_image, player1j, WIDTH, HEIGHT, BLACK, load_ground
from geo.jump import JUMP_VELOCITY, manage_jump

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("FLappy Bird")



pygame.font.init()
my_font = pygame.font.SysFont('Arial', 30)

ground_width = GROUND.get_width()
ground_height = GROUND.get_height()
ground_x = 0
ground_speed = 3
LEVEL_SQUARE_COLORS = {
    1: (40, 130, 220),
    2: (220, 110, 30),
    3: (145, 55, 190),
    4: (45, 150, 70),
}
LEVEL_BACKGROUND_COLORS = {
    1: (220, 245, 255),
    2: (255, 238, 210),
    3: (245, 225, 255),
    4: (225, 250, 225),
}

def main():
    global ground_x, ground_speed, player_image, player1j, spikes, BLACK, level_text, my_font, screen, WIDTH, HEIGHT, WHITE, GROUND, ground_width, ground_height
    clock = pygame.time.Clock()
    points = 0
    current_level = 1
    bird_x = player_image.get_height() + ground_height
    bird_ground_y = HEIGHT - ground_height - player_image.get_height() + 1
    bird_y = float(bird_ground_y)
    bird_velocity = 0.0
    spikes_image_path = Path(__file__).resolve().parent / "spikes.png"
    spike_sheet = pygame.image.load(str(spikes_image_path)).convert_alpha()
    spike_sprites = []
    for x, top in ((30, 40), (180, 40), (330, 30), (480, 20), (630, 20)):
        sprite = spike_sheet.subsurface(pygame.Rect(x, top, 130, 160 - top)).copy()
        spike_sprites.append(
            pygame.transform.scale(sprite, (sprite.get_width() // 2, sprite.get_height() // 2))
        )
    spikes = []
    platforms = []
    platform_size = 50
    next_platform_time = pygame.time.get_ticks() + random.randint(1500, 3000)
    standing_platform = None
    next_spike_time = pygame.time.get_ticks() + random.randint(1000, 4500)

    run = True

    while run:
        palette_level = min(current_level, 4)
        screen.fill(LEVEL_BACKGROUND_COLORS[palette_level])

        # Move ground left
        ground_x -= ground_speed
        if ground_x <= -ground_width:
            ground_x = 0

        current_time = pygame.time.get_ticks()
        if current_time >= next_spike_time:
            spikes.append([random.choice(spike_sprites), float(WIDTH), False])
            next_spike_time = current_time + random.randint(1000, 2500)

        if current_time >= next_platform_time:
            ground_top = HEIGHT - ground_height
            platform_y = ground_top - platform_size
            platforms.append([float(WIDTH), platform_y])
            next_platform_time = current_time + random.randint(1600, 3000)

        for platform in platforms:
            platform[0] -= ground_speed
            platform_rect = pygame.Rect(
                int(platform[0]), platform[1], platform_size, platform_size
            )
            pygame.draw.rect(
                screen, LEVEL_SQUARE_COLORS[palette_level], platform_rect
            )
            pygame.draw.rect(screen, BLACK, platform_rect, 2)
        platforms = [platform for platform in platforms if platform[0] + platform_size > 0]

        if standing_platform is not None:
            if (
                bird_x + player_image.get_width() > standing_platform[0]
                and bird_x < standing_platform[0] + platform_size
            ):
                bird_y = float(standing_platform[1] - player_image.get_height())
            else:
                standing_platform = None

        for spike in spikes:
            spike[1] -= ground_speed
            if not spike[2] and spike[1] + spike[0].get_width() < bird_x:
                spike[2] = True
                points += 1
            screen.blit(
                spike[0],
                (int(spike[1]), HEIGHT - ground_height - spike[0].get_height()),
            )
        spikes = [spike for spike in spikes if spike[1] + spike[0].get_width() > 0]
        bird_rect = player_image.get_rect(topleft=(bird_x, int(bird_y*0.5)))
        bird_rect2 = player1j.get_rect(topleft=(bird_x, int(bird_y)))
        for spike_image, spike_x, _ in spikes:
            spike_rect = spike_image.get_rect(
                topleft=(
                    int(spike_x),
                    HEIGHT - ground_height - spike_image.get_height(),
                )
            )
            if bird_rect.colliderect(spike_rect) or bird_rect2.colliderect(spike_rect):
                run = False
                print("Game Over! You hit a spike.")
                break
        new_level = points // 10 + 1
        if new_level != current_level:
            current_level = new_level
            GROUND = load_ground(current_level)
            ground_width = GROUND.get_width()
            ground_height = GROUND.get_height()
            ground_x %= ground_width
            bird_ground_y = HEIGHT - ground_height - player_image.get_height() + 1
            ground_speed = 3 + (current_level - 1) * 0.5

        # Draw ground twice so it loops seamlessly
        screen.blit(GROUND, (ground_x, HEIGHT - ground_height))
        screen.blit(GROUND, (ground_x + ground_width, HEIGHT - ground_height))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif manage_jump(
                event, standing_platform is not None or bird_y >= bird_ground_y
            ):
                bird_velocity = JUMP_VELOCITY
                standing_platform = None

        previous_bottom = bird_y + player_image.get_height()
        bird_y += bird_velocity
        landed = standing_platform is not None
        if not landed and bird_velocity >= 0:
            bird_rect = pygame.Rect(
                bird_x, int(bird_y), player_image.get_width(), player_image.get_height()
            )
            for platform in platforms:
                platform_rect = pygame.Rect(
                    int(platform[0]), platform[1], platform_size, platform_size
                )
                if (
                    previous_bottom <= platform_rect.top
                    and bird_rect.bottom >= platform_rect.top
                    and bird_rect.right > platform_rect.left
                    and bird_rect.left < platform_rect.right
                ):
                    bird_y = float(platform_rect.top - player_image.get_height())
                    bird_velocity = 0.0
                    standing_platform = platform
                    landed = True
                    break

        if landed:
            bird_velocity = 0.0

        if not landed:
            if bird_y < bird_ground_y:
                bird_velocity += 0.5
            else:
                bird_y = float(bird_ground_y)
                bird_velocity = 0.0
                standing_platform = None
        
            

        bird_sprite = player_image if bird_y == bird_ground_y else player1j
        screen.blit(bird_sprite, (bird_x, int(bird_y)))
        score_text = my_font.render(f"Points: {points}", True, BLACK)
        level_text = my_font.render(f"Level: {points // 10 + 1}", True, BLACK)
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (10, 40))

        if level_text == 5:
                run = False
                print("Congratulations! You've reached level 5 and won the game!")
                end_text = my_font.render(f"Congratulations! You've reached level 5 and won the game!", True, BLACK)

        pygame.display.flip()
                    

        
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()