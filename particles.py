import pygame
import random

class Particle:
    def __init__(self, x, y, color, width, height, lifetime=18, particle_type="normal", arena_bounds=None):
        self.x = float(x)
        self.y = float(y)
        self.dx = random.uniform(-3.5, 3.5)
        self.dy = random.uniform(-3.5, 3.5)
        self.color = color
        self.base_color = color  # store original color
        self.width = width
        self.height = height
        self.age = 0
        self.lifetime = lifetime
        self.particle_type = particle_type
        
        # Physics properties
        self.bounce_factor = 0.6  # energy retained after bounce
        self.gravity = 0.0
        self.air_resistance = 0.98
        self.arena_bounds = arena_bounds  # (x, y, width, height) of arena
        self.bounced = False  # track if particle has bounced
        
        # Type-specific properties
        if particle_type == "spark":
            self.dx = random.uniform(-5.0, 5.0)
            self.dy = random.uniform(-5.0, 5.0) 
            self.lifetime = max(12, lifetime // 2)
            self.bounce_factor = 0.8  # sparks bounce more
            self.gravity = 0.05  # light gravity
        elif particle_type == "explosion":
            speed = random.uniform(2.0, 6.0)
            angle = random.uniform(0, 6.28318)  # 2π radians
            self.dx = speed * random.uniform(0.8, 1.2) * (1 if random.random() > 0.5 else -1)
            self.dy = speed * random.uniform(0.8, 1.2) * (1 if random.random() > 0.5 else -1)
            self.bounce_factor = 0.4  # explosion debris bounces less
            self.gravity = 0.15  # heavier gravity
        elif particle_type == "trail":
            self.dx *= 0.3  # slower movement for trail particles
            self.dy *= 0.3
            self.bounce_factor = 0.2  # trail particles barely bounce
            self.gravity = 0.02  # very light gravity

    @property
    def dead(self):
        return self.age >= self.lifetime

    def update(self, wind_force=(0, 0)):
        # Apply gravity
        self.dy += self.gravity
        
        # Apply wind force
        self.dx += wind_force[0]
        self.dy += wind_force[1]
        
        # Update position
        self.x += self.dx
        self.y += self.dy
        
        # Arena collision detection and bouncing
        if self.arena_bounds:
            arena_x, arena_y, arena_w, arena_h = self.arena_bounds
            
            # Left/right wall collision
            if self.x <= arena_x or self.x >= arena_x + arena_w:
                self.dx *= -self.bounce_factor
                self.x = max(arena_x, min(arena_x + arena_w, self.x))
                self.bounced = True
                
                # Add some randomness to bounce direction
                self.dy += random.uniform(-0.5, 0.5)
                
            # Top/bottom wall collision  
            if self.y <= arena_y or self.y >= arena_y + arena_h:
                self.dy *= -self.bounce_factor
                self.y = max(arena_y, min(arena_y + arena_h, self.y))
                self.bounced = True
                
                # Add some randomness to bounce direction
                self.dx += random.uniform(-0.5, 0.5)
        
        # Apply air resistance
        self.dx *= self.air_resistance
        self.dy *= self.air_resistance
        
        # Reduce lifetime faster if bounced (particles lose energy)
        if self.bounced:
            self.age += 1.2
        else:
            self.age += 1
        
        # Update color for some particle types
        if self.particle_type == "spark" and self.age > self.lifetime // 3:
            # Sparks fade from white/yellow to red/orange
            progress = (self.age - self.lifetime // 3) / (self.lifetime * 2 // 3)
            red = max(255, int(255 * (1 - progress * 0.3)))
            green = max(0, int(255 * (1 - progress)))
            blue = max(0, int(self.base_color[2] * (1 - progress)))
            self.color = (red, green, blue)
        elif self.particle_type == "explosion" and self.bounced:
            # Explosion particles get darker when they bounce
            fade_factor = 0.9
            self.color = tuple(int(c * fade_factor) for c in self.color)

    def draw(self, screen, offset=(0, 0)):
        # Calculate scale and alpha based on age
        life_left = max(self.lifetime - self.age, 0)
        scale = max(life_left / self.lifetime, 0)
        
        # Type-specific drawing
        if self.particle_type == "spark":
            # Sparks are small bright rectangles that fade quickly
            w = max(int(self.width * scale * 0.7), 1)
            h = max(int(self.height * scale * 0.7), 1)
            pygame.draw.rect(
                screen,
                self.color,
                (int(self.x) + offset[0] - w // 2, int(self.y) + offset[1] - h // 2, w, h)
            )
        elif self.particle_type == "explosion":
            # Explosion particles are larger and shrink more dramatically
            w = max(int(self.width * scale * scale), 1)  # double scale effect
            h = max(int(self.height * scale * scale), 1)
            pygame.draw.rect(
                screen,
                self.color,
                (int(self.x) + offset[0] - w // 2, int(self.y) + offset[1] - h // 2, w, h)
            )
        else:
            # Normal particles - original behavior
            w = max(int(self.width * scale), 1)
            h = max(int(self.height * scale), 1)
            pygame.draw.rect(
                screen,
                self.color,
                (int(self.x) + offset[0] - w // 2, int(self.y) + offset[1] - h // 2, w, h)
            )


class ParticleSystem:
    """Enhanced particle system with physics and environmental effects"""
    
    def __init__(self, arena_bounds=None):
        self.particles = []
        self.arena_bounds = arena_bounds
        self.wind_force = (0, 0)  # global wind effect
        self.wind_timer = 0
    
    def set_arena_bounds(self, x, y, width, height):
        """Set arena boundaries for particle collision"""
        self.arena_bounds = (x, y, width, height)
    
    def clear(self):
        """Clear all particles"""
        self.particles = []
    
    def update(self):
        """Update all particles with physics and remove dead ones"""
        # Update wind effect (subtle, random changes)
        self.wind_timer += 1
        if self.wind_timer % 60 == 0:  # change wind every second
            self.wind_force = (
                random.uniform(-0.02, 0.02),  # very subtle horizontal wind
                random.uniform(-0.01, 0.01)   # very subtle vertical wind
            )
        
        # Update all particles
        for particle in self.particles:
            particle.update(self.wind_force)
        self.particles = [p for p in self.particles if not p.dead]
    
    def draw(self, screen, offset=(0, 0)):
        """Draw all particles"""
        for particle in self.particles:
            particle.draw(screen, offset)
    
    def add_explosion(self, x, y, color, count=20):
        """Add explosion particles at the given position"""
        for _ in range(count):
            self.particles.append(Particle(x, y, color, 12, 12, lifetime=28, 
                                         particle_type="explosion", arena_bounds=self.arena_bounds))
        # Add some sparks for extra effect
        for _ in range(count // 3):
            self.particles.append(Particle(x, y, (255, 255, 255), 8, 8, lifetime=20, 
                                         particle_type="spark", arena_bounds=self.arena_bounds))
    
    def add_collision_sparks(self, x, y, count=8):
        """Add bright sparks for collision feedback"""
        for _ in range(count):
            self.particles.append(Particle(x, y, (255, 255, 255), 6, 6, lifetime=15, 
                                         particle_type="spark", arena_bounds=self.arena_bounds))
    
    def add_damage_sparks(self, x, y, color, count=6):
        """Add colored sparks when fighter takes damage"""
        for _ in range(count):
            self.particles.append(Particle(x, y, color, 8, 8, lifetime=18, 
                                         particle_type="spark", arena_bounds=self.arena_bounds))
    
    def add_pickup_glow(self, x, y, color, count=8):
        """Add glowing effect when pickup is collected"""
        for _ in range(count):
            self.particles.append(Particle(x, y, color, 10, 10, lifetime=25, 
                                         particle_type="trail", arena_bounds=self.arena_bounds))
    
    def add_wall_sparks(self, x, y, count=4):
        """Add sparks when particles hit walls"""
        for _ in range(count):
            self.particles.append(Particle(x, y, (255, 200, 100), 4, 4, lifetime=12, 
                                         particle_type="spark", arena_bounds=self.arena_bounds))
