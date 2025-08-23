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
        
        # Movement trails
        self.trail_positions = []  # stores (x, y, age) tuples
        self.max_trail_length = 8
        self.trail_spacing = 3  # add trail point every N frames
        self.trail_counter = 0

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
            
        # Update trail positions
        self.trail_counter += 1
        if self.trail_counter >= self.trail_spacing:
            # Add current position to trail
            center_x = self.x + self.width // 2
            center_y = self.y + self.height // 2
            self.trail_positions.append((center_x, center_y, 0))
            self.trail_counter = 0
            
        # Age existing trail points and remove old ones
        self.trail_positions = [(x, y, age + 1) for x, y, age in self.trail_positions 
                               if age < self.max_trail_length]

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
        # Draw trail first (behind fighter)
        self._draw_trail(screen, offset)
        
        # Determine fighter color
        if self.invincible:
            color = self._invincible_color()
        elif self.hurt_timer > 0 and (self.hurt_timer % self.blink_period) < (self.blink_period // 2):
            color = (255, 255, 255)
        else:
            color = self.base_color

        # Draw fighter
        pygame.draw.rect(
            screen,
            color,
            (self.x + offset[0], self.y + offset[1], self.width, self.height)
        )
        
    def _draw_trail(self, screen, offset=(0, 0)):
        """Draw the movement trail behind the fighter"""
        for i, (x, y, age) in enumerate(self.trail_positions):
            # Calculate alpha/size based on age (older = more transparent/smaller)
            alpha = max(0, 255 - (age * 32))  # fade out over time
            size = max(2, self.width // 2 - age * 2)  # shrink over time
            
            if alpha <= 0:
                continue
                
            # Create a darker version of the fighter's color for the trail
            trail_color = tuple(max(0, int(c * 0.6)) for c in self.base_color)
            
            # Create surface with alpha for trail segment
            trail_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            trail_surf.fill((*trail_color, alpha))
            
            # Draw trail segment centered on position
            screen.blit(trail_surf, 
                       (x - size // 2 + offset[0], y - size // 2 + offset[1]))

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
