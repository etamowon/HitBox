import pygame
import random

class Particle:
    def __init__(self, x, y, color, width, height, lifetime=18):
        self.x = float(x)
        self.y = float(y)
        self.dx = random.uniform(-3.5, 3.5)
        self.dy = random.uniform(-3.5, 3.5)
        self.color = color
        self.width = width
        self.height = height
        self.age = 0
        self.lifetime = lifetime

    @property
    def dead(self):
        return self.age >= self.lifetime

    def update(self):
        # simple motion + slight drag
        self.x += self.dx
        self.y += self.dy
        self.dx *= 0.92
        self.dy *= 0.92
        self.age += 1

    def draw(self, screen, offset=(0, 0)):
        # Option A: shrink as it ages (simple "disappear" without alpha)
        life_left = max(self.lifetime - self.age, 0)
        scale = max(life_left / self.lifetime, 0)
        w = max(int(self.width * scale), 1)
        h = max(int(self.height * scale), 1)
        pygame.draw.rect(
            screen,
            self.color,
            (int(self.x) + offset[0] - w // 2, int(self.y) + offset[1] - h // 2, w, h)
        )
