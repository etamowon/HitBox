import pygame

class Fighter:
    def __init__(self, x, y, dx, dy, width, height, color, health,
                 arena_x, arena_y, arena_width, arena_height):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.width = width
        self.height = height
        self.base_color = color

        # Health
        self.max_health = health
        self.health = health
        self.displayed_health = health

        # Arena boundaries
        self.arena_x = arena_x
        self.arena_y = arena_y
        self.arena_width = arena_width
        self.arena_height = arena_height

        # Effects
        self.invincible = False
        self.invincible_timer = 0   # frames remaining for invincibility
        self.hurt_timer = 0
        self.hurt_flash_frames = 8
        self.blink_period = 4

    def move(self):
        self.x += self.dx
        self.y += self.dy

        # Bounce off arena walls
        if self.x <= self.arena_x or self.x + self.width >= self.arena_x + self.arena_width:
            self.dx *= -1
        if self.y <= self.arena_y or self.y + self.height >= self.arena_y + self.arena_height:
            self.dy *= -1

    def update_effects(self):
        # Hurt flash
        if self.hurt_timer > 0:
            self.hurt_timer -= 1

        # Invincibility timer
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
            self.invincible = True
        else:
            self.invincible = False

    def _invincible_color(self):
        # Simple Mario-style cycling
        palette = [
            (255, 255, 255),
            (255, 0, 0),
            (255, 165, 0),
            (255, 255, 0),
            (0, 255, 0),
            (0, 255, 255),
            (0, 128, 255),
            (170, 0, 255),
            (255, 105, 180),
        ]
        # Cycle fast: change every 2 frames
        idx = ((self.invincible_timer // 2) % len(palette))
        return palette[idx]

    def draw(self, screen, offset=(0, 0)):
        if self.invincible:
            color = self._invincible_color()
        elif self.hurt_timer > 0 and (self.hurt_timer % self.blink_period) < (self.blink_period // 2):
            color = (255, 255, 255)
        else:
            color = self.base_color

        pygame.draw.rect(
            screen,
            color,
            (self.x + offset[0], self.y + offset[1], self.width, self.height)
        )

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def collides_with(self, other):
        return self.get_rect().colliderect(other.get_rect())

    def take_damage(self, amount):
        if self.invincible or amount <= 0:
            return 0
        old = self.health
        self.health = max(0, self.health - amount)
        applied = old - self.health
        if applied > 0:
            self.hurt_timer = self.hurt_flash_frames
        return applied

    def grant_invincibility(self, frames):
        self.invincible_timer = max(self.invincible_timer, frames)
        self.invincible = True

    def heal(self, amount):
        if amount <= 0:
            return
        self.health = min(self.max_health, self.health + amount)
