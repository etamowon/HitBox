import pygame
import random

# === Setup ===
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 500
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# === Arena Settings ===
ARENA_MARGIN = 50
ARENA_WIDTH = SCREEN_WIDTH - 2 * ARENA_MARGIN
ARENA_HEIGHT = 300
ARENA_X = ARENA_MARGIN
ARENA_Y = ARENA_MARGIN
OUTLINE_THICKNESS = 5

# === Fighter Settings ===
FIGHTER_WIDTH = 50
FIGHTER_HEIGHT = 50
x = random.randint(ARENA_X, ARENA_X + ARENA_WIDTH - FIGHTER_WIDTH)
y = random.randint(ARENA_Y, ARENA_Y + ARENA_HEIGHT - FIGHTER_HEIGHT)
dx = 4
dy = 3

# === Invincibility Color Cycle Settings ===
colors = ["red", "orange", "yellow", "green", "blue", "purple"]
color_index = 0
color_change_delay = 100  # ms
last_color_change = pygame.time.get_ticks()
color = colors[color_index]  # Initial color

# === Main Game Loop ===
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # === Move Fighter ===
    x += dx
    y += dy

    # === Bounce Inside Arena ===
    if x <= ARENA_X or x + FIGHTER_WIDTH >= ARENA_X + ARENA_WIDTH:
        dx *= -1
    if y <= ARENA_Y or y + FIGHTER_HEIGHT >= ARENA_Y + ARENA_HEIGHT:
        dy *= -1

    # === Update Color (Invincibility Effect) ===
    current_time = pygame.time.get_ticks()
    if current_time - last_color_change > color_change_delay:
        color_index = (color_index + 1) % len(colors)
        color = colors[color_index]
        last_color_change = current_time

    # === Drawing ===
    screen.fill("black")

    # White outline
    pygame.draw.rect(
        screen, "white",
        (
            ARENA_X - OUTLINE_THICKNESS,
            ARENA_Y - OUTLINE_THICKNESS,
            ARENA_WIDTH + 2 * OUTLINE_THICKNESS,
            ARENA_HEIGHT + 2 * OUTLINE_THICKNESS
        )
    )

    # Arena background
    pygame.draw.rect(screen, "black", (ARENA_X, ARENA_Y, ARENA_WIDTH, ARENA_HEIGHT))

    # Draw Fighter
    pygame.draw.rect(screen, color, (x, y, FIGHTER_WIDTH, FIGHTER_HEIGHT))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

