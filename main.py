import pygame 
import random
import math
from fighter import Fighter
from particles import Particle, ParticleSystem

# === Setup ===
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 500
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("HitBox")
clock = pygame.time.Clock()

# === Arena Settings ===
ARENA_MARGIN = 50
ARENA_WIDTH = SCREEN_WIDTH - 2 * ARENA_MARGIN
ARENA_HEIGHT = 300
ARENA_X = ARENA_MARGIN
ARENA_Y = ARENA_MARGIN
OUTLINE_THICKNESS = 5

# === Combat Tuning ===
DAMAGE = 10  # collision damage; Health pickup heals by this amount too

# === Fighter Settings ===
FIGHTER_SIZE = 50
FIGHTER_WIDTH = FIGHTER_SIZE
FIGHTER_HEIGHT = FIGHTER_SIZE
dx = 4
dy = 3
health = 100

# === Health Bar Settings ===
HEALTH_BAR_WIDTH = 240
HEALTH_BAR_HEIGHT = 40
BLUE_BAR_X = ARENA_X
RED_BAR_X = ARENA_X + ARENA_WIDTH - HEALTH_BAR_WIDTH
BLUE_BAR_Y = ARENA_Y + ARENA_HEIGHT + 30
RED_BAR_Y = BLUE_BAR_Y

# === Fonts ===
font_big    = pygame.font.Font("assets/fonts/PressStart2P.ttf", 72)
font_title  = pygame.font.Font("assets/fonts/PressStart2P.ttf", 56)
font_result = pygame.font.Font("assets/fonts/PressStart2P.ttf", 48)
font_item   = pygame.font.Font("assets/fonts/PressStart2P.ttf", 42)
font_label  = pygame.font.Font("assets/fonts/PressStart2P.ttf", 20)
font_small  = pygame.font.Font("assets/fonts/PressStart2P.ttf", 18)
# Select screen fonts
font_select_head = pygame.font.Font("assets/fonts/PressStart2P.ttf", 32)
font_select_hint = pygame.font.Font("assets/fonts/PressStart2P.ttf", 20)

# === Game States ===
STATE_SPLASH         = -1
STATE_SELECT         = -2
STATE_PLAYING        = 0
STATE_PAUSED         = 1
STATE_GAMEOVER_TRANS = 2   # blur/fade + point-count animation
STATE_GAMEOVER       = 3   # menu fades in here
state = STATE_SPLASH

# === Transition (retro checkerboard) ===
class Transition:
    def __init__(self):
        self.active = False
        self.t = 0
        self.duration = 30   # frames
        self.next_state = None
        self.phase = "out"   # "out" -> switch -> "in"
        # checkerboard grid size
        self.tile = 24
        self.cols = (SCREEN_WIDTH  + self.tile - 1) // self.tile
        self.rows = (SCREEN_HEIGHT + self.tile - 1) // self.tile

    def start(self, duration_frames, next_state):
        self.active = True
        self.t = 0
        self.duration = max(1, duration_frames)
        self.next_state = next_state
        self.phase = "out"

    def update(self):
        if not self.active: return
        self.t += 1
        if self.t >= self.duration:
            if self.phase == "out":
                switch_state(self.next_state)
                self.phase = "in"
                self.t = 0
            else:
                self.active = False

    def _draw_checker_phase(self, surf, p, invert=False):
        for parity in (0, 1):
            prog = max(0.0, min(1.0, p * 2.0 - parity))
            if prog <= 0: 
                continue
            max_row = int(self.rows * prog + 0.999)
            for j in range(max_row):
                for i in range(self.cols):
                    if ((i + j) & 1) != parity:
                        continue
                    x = i * self.tile
                    y = j * self.tile
                    if not invert:
                        pygame.draw.rect(surf, (0,0,0), (x, y, self.tile, self.tile))
        if invert:
            overlay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            overlay.fill((0,0,0,255))
            for parity in (0, 1):
                prog = max(0.0, min(1.0, p * 2.0 - parity))
                max_row = int(self.rows * prog + 0.999)
                for j in range(max_row):
                    for i in range(self.cols):
                        if ((i + j) & 1) != parity: 
                            continue
                        x = i * self.tile
                        y = j * self.tile
                        pygame.draw.rect(overlay, (0,0,0,0), (x, y, self.tile, self.tile))
            surf.blit(overlay, (0,0))

    def draw_overlay(self, surf):
        if not self.active: return
        progress = self.t / self.duration
        if self.phase == "out":
            self._draw_checker_phase(surf, progress, invert=False)
        else:
            self._draw_checker_phase(surf, progress, invert=True)

transition = Transition()

# === Pause Menu ===
pause_menu_items = ["Resume", "Quit"]
pause_menu_index = 0
blurred_bg_pause = None

# === Gameover (visuals) ===
gameover_menu_items = ["Play Again", "Quit"]
gameover_menu_index = 0
result_text = ""
result_color = (255,255,255)
GO_FADE_FRAMES = 54
go_fade_t = 0
go_menu_alpha = 0   # menu fades in during STATE_GAMEOVER

# === Shake ===
shake_timer = 0
shake_intensity = 1.0  # multiplier for shake strength
shake_offset = [0, 0]

# === Enhanced Particle System ===
particle_system = ParticleSystem()
damage_texts = []

# === Sound System ===
class SoundManager:
    """Sound system with placeholder functions for future audio implementation"""
    
    def __init__(self):
        self.enabled = True
        self.volume = 0.7
        # Initialize pygame mixer for when sounds are added
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.mixer_available = True
        except pygame.error:
            self.mixer_available = False
            print("Sound mixer not available")
    
    def play_collision(self, intensity=1.0):
        """Play collision sound - placeholder for future implementation"""
        if self.enabled and self.mixer_available:
            # Placeholder: print what sound would play
            if intensity > 1.5:
                pass  # Would play heavy impact sound
            else:
                pass  # Would play normal collision sound
    
    def play_explosion(self):
        """Play explosion sound - placeholder for future implementation"""
        if self.enabled and self.mixer_available:
            pass  # Would play explosion sound
    
    def play_pickup(self, pickup_type="health"):
        """Play pickup collection sound - placeholder for future implementation"""
        if self.enabled and self.mixer_available:
            pass  # Would play pickup sound based on type
    
    def play_menu_select(self):
        """Play menu selection sound - placeholder for future implementation"""
        if self.enabled and self.mixer_available:
            pass  # Would play menu beep sound
    
    def play_menu_navigate(self):
        """Play menu navigation sound - placeholder for future implementation"""
        if self.enabled and self.mixer_available:
            pass  # Would play navigation sound
    
    def play_game_start(self):
        """Play game start sound - placeholder for future implementation"""
        if self.enabled and self.mixer_available:
            pass  # Would play game start fanfare
    
    def play_round_end(self, result="win"):
        """Play round end sound - placeholder for future implementation"""
        if self.enabled and self.mixer_available:
            pass  # Would play win/lose/draw sound based on result
    
    def set_volume(self, volume):
        """Set master volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        if self.mixer_available:
            pygame.mixer.music.set_volume(self.volume)
    
    def toggle_sound(self):
        """Toggle sound on/off"""
        self.enabled = not self.enabled
        return self.enabled

sound_manager = SoundManager()

# === Visual Feedback ===
pickup_flashes = []  # stores (x, y, timer, color) for pickup collection flashes

# === Damage Text ===
class DamageText:
    def __init__(self, x, y, amount, color=(255, 255, 255), lifetime=32):
        self.x = float(x); self.y = float(y)
        self.vx = random.uniform(-0.3, 0.3); self.vy = -1.3
        self.age = 0; self.lifetime = lifetime
        self.amount = int(amount); self.color = color
        self.font = pygame.font.Font("assets/fonts/PressStart2P.ttf", 28)
        self.jitter = 0.15
    @property
    def dead(self): return self.age >= self.lifetime
    def update(self):
        self.x += self.vx + random.uniform(-self.jitter, self.jitter)
        self.y += self.vy; self.vy *= 0.96; self.age += 1
    def draw(self, screen, offset=(0,0)):
        left = max(0, self.lifetime - self.age)
        alpha = int(255 * (left / self.lifetime))
        surf = self.font.render(str(self.amount), True, self.color)
        surf.set_alpha(alpha)
        screen.blit(surf, (int(self.x)+offset[0], int(self.y)+offset[1]))

# === Score System ===
current_score = 100
high_score = 100
POINT_WIN = 25
POINT_LOSS = -25
points_delta = 0            # +25 / -25 / 0 (draw)
delta_color = (255, 255, 255) # white for loss or draw, yellow for gain
delta_count_value = 0       # animated count shown during GAMEOVER_TRANS

def pad6(n):  # zero-padded like retro counters
    return f"{max(0,n):06d}"

def draw_scoreboard(show_high=True):
    # top-left: SCORE
    score_surf = font_small.render(f"SCORE {pad6(current_score)}", True, (255,255,255))
    screen.blit(score_surf, (8, 8))
    if show_high:
        hi_surf = font_small.render(f"HI {pad6(high_score)}", True, (255,255,255))
        hw, _ = hi_surf.get_size()
        screen.blit(hi_surf, (SCREEN_WIDTH - hw - 8, 8))

# === UI Helpers ===
def draw_health_bar(screen, x, y, current, displayed, max_health, color, offset, align="left"):
    OUTLINE_PADDING = 4; FILL_PADDING = 5
    x += offset[0]; y += offset[1]
    pygame.draw.rect(screen, (255,255,255), (x, y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT))
    inner_x = x + OUTLINE_PADDING; inner_y = y + OUTLINE_PADDING
    inner_w = HEALTH_BAR_WIDTH - 2*OUTLINE_PADDING; inner_h = HEALTH_BAR_HEIGHT - 2*OUTLINE_PADDING
    pygame.draw.rect(screen, (0,0,0), (inner_x, inner_y, inner_w, inner_h))
    usable_w = inner_w - 2*FILL_PADDING
    disp_w = int(usable_w * max(0, min(displayed, max_health))/max_health)
    curr_w = int(usable_w * max(0, min(current,  max_health))/max_health)
    fy = inner_y + FILL_PADDING; fh = inner_h - 2*FILL_PADDING
    if align == "left":
        bx = inner_x + FILL_PADDING
        pygame.draw.rect(screen, (255,255,255), (bx, fy, disp_w, fh))
        pygame.draw.rect(screen, color,           (bx, fy, curr_w, fh))
    else:
        tx = inner_x + inner_w - FILL_PADDING - disp_w
        cx = inner_x + inner_w - FILL_PADDING - curr_w
        pygame.draw.rect(screen, (255,255,255), (tx, fy, disp_w, fh))
        pygame.draw.rect(screen, color,          (cx, fy, curr_w, fh))

def draw_centered_label(text, bar_x, bar_y, bar_w, color, offset):
    label = font_label.render(text, True, color)
    lw, _ = label.get_size()
    x = bar_x + offset[0] + (bar_w - lw)//2
    y = bar_y + offset[1] + HEALTH_BAR_HEIGHT + 6
    screen.blit(label, (x, y))

def update_health_bar_value(f):
    speed = 1
    if f.displayed_health > f.health:
        f.displayed_health = max(f.health, f.displayed_health - speed)
    elif f.displayed_health < f.health:
        f.displayed_health = min(f.health, f.displayed_health + speed)

def fast_blur(surf, scale=0.22, passes=2):
    if passes < 1: return surf.copy()
    w, h = surf.get_size()
    sw = max(1, int(w*scale)); sh = max(1, int(h*scale))
    work = surf
    for _ in range(passes):
        work = pygame.transform.smoothscale(work, (sw, sh))
        work = pygame.transform.smoothscale(work, (w, h))
    return work

def draw_pause_menu(screen, blurred_bg, items, idx):
    screen.blit(blurred_bg, (0,0))
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0,0,0,140)); screen.blit(overlay, (0,0))
    sw, sh = screen.get_size()
    t = font_title.render("Paused", True, (255,255,255))
    tw, th = t.get_size(); screen.blit(t, (sw//2 - tw//2, sh//2 - 160))
    start_y = sh//2 - 40; gap = 54
    for i, txt in enumerate(items):
        sel = (i == idx); col = (255,255,255) if sel else (200,200,200)
        it = font_item.render(txt, True, col); iw, ih = it.get_size()
        screen.blit(it, (sw//2 - iw//2, start_y + i*gap))
        if sel:
            ptr = font_item.render(">", True, col); pw,_ = ptr.get_size()
            screen.blit(ptr, (sw//2 - iw//2 - pw - 12, start_y + i*gap))

def draw_gameover_overlay(screen, progress, show_menu, menu_alpha):
    # blurred frame underneath
    frame = screen.copy()
    blurred = fast_blur(frame, scale=0.22, passes=2)
    alpha = int(255 * progress)
    blurred.set_alpha(alpha)
    screen.blit(blurred, (0,0))
    shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    shade.fill((0,0,0, int(160*progress)))
    screen.blit(shade, (0,0))

    # Header text ("YOU WON/LOST/DRAW") in player's chosen color
    sw, sh = screen.get_size()
    head = font_result.render(result_text, True, result_color)
    head.set_alpha(alpha)
    hw, hh = head.get_size()
    screen.blit(head, (sw//2 - hw//2, sh//2 - 170))

    # Points delta count (visible before menu shows; persists under menu)
    sign = "+" if points_delta > 0 else ""
    count_to_show = delta_count_value if progress < 1.0 else abs(points_delta)
    delta_txt = f"{sign}{count_to_show}"
    col = delta_color
    delta_s = font_item.render(delta_txt, True, col)
    dw, dh = delta_s.get_size()
    # place just below header
    screen.blit(delta_s, (sw//2 - dw//2, sh//2 - 110))

    # Menu items (fade-in alpha)
    if show_menu:
        start_y = sh//2 - 30; gap = 54
        for i, txt in enumerate(gameover_menu_items):
            sel = (i == gameover_menu_index)
            base_col = (255,255,255) if sel else (200,200,200)
            it = font_item.render(txt, True, base_col)
            it.set_alpha(menu_alpha)
            iw, ih = it.get_size()
            screen.blit(it, (sw//2 - iw//2, start_y + i*gap))
            if sel:
                ptr = font_item.render(">", True, base_col)
                ptr.set_alpha(menu_alpha)
                pw,_ = ptr.get_size()
                screen.blit(ptr, (sw//2 - iw//2 - pw - 12, start_y + i*gap))

def draw_pickup_flashes(screen, offset=(0,0)):
    """Draw expanding ring effects for pickup collection"""
    for x, y, timer, color in pickup_flashes:
        if timer > 0:
            # Draw expanding ring
            radius = int((20 - timer) * 2)  # expands as timer decreases
            alpha = int(255 * (timer / 20))  # fades as timer decreases
            if radius > 0 and alpha > 0:
                # Create surface with alpha
                ring_surf = pygame.Surface((radius*4, radius*4), pygame.SRCALPHA)
                pygame.draw.circle(ring_surf, (*color, alpha), (radius*2, radius*2), radius, 3)
                screen.blit(ring_surf, (x - radius*2 + offset[0], y - radius*2 + offset[1]))

# === Pickups ===
class Pickup:
    RADIUS = 14
    LIFETIME = 6 * 60

    def __init__(self, cx, cy):
        self.cx = cx; self.cy = cy
        self.age = 0
        d = self.RADIUS * 2
        self.rect = pygame.Rect(cx - self.RADIUS, cy - self.RADIUS, d, d)

    @property
    def dead(self): return self.age >= self.LIFETIME
    def update(self): self.age += 1
    def colliding_fighters(self, f1, f2):
        hits = []
        if self.rect.colliderect(f1.get_rect()): hits.append(1)
        if self.rect.colliderect(f2.get_rect()): hits.append(2)
        return hits
    def apply(self, fighter): raise NotImplementedError
    def draw(self, screen, offset=(0,0)): raise NotImplementedError

class HealthPickup(Pickup):
    def apply(self, fighter): 
        fighter.heal(DAMAGE)
        # Create pickup glow effect
        particle_system.add_pickup_glow(self.cx, self.cy, (34, 197, 94))
        
    def draw(self, screen, offset=(0,0)):
        x = self.cx + offset[0]; y = self.cy + offset[1]
        pygame.draw.circle(screen, (34,197,94), (x,y), self.RADIUS)
        pygame.draw.circle(screen, (20,20,20), (x,y), self.RADIUS, 2)
        arm = self.RADIUS // 2 + 2; thick = 4
        pygame.draw.rect(screen, (255,255,255), (x - thick//2, y - arm, thick, 2*arm))
        pygame.draw.rect(screen, (255,255,255), (x - arm, y - thick//2, 2*arm, thick))

class InvincibilityPickup(Pickup):
    DURATION_FRAMES = 5 * 60
    def apply(self, fighter): 
        fighter.grant_invincibility(self.DURATION_FRAMES)
        # Create pickup glow effect
        particle_system.add_pickup_glow(self.cx, self.cy, (255, 255, 255))
        
    def draw(self, screen, offset=(0,0)):
        x = self.cx + offset[0]; y = self.cy + offset[1]
        palette = [(255,255,255),(255,0,0),(255,165,0),(255,255,0),
                   (0,255,0),(0,255,255),(0,128,255),(170,0,255),(255,105,180)]
        idx = (self.age // 3) % len(palette)
        pygame.draw.circle(screen, palette[idx], (x,y), self.RADIUS)
        pygame.draw.circle(screen, (20,20,20), (x,y), self.RADIUS, 2)

pickups = []
pickup_spawn_cooldown = 0
PICKUP_COOLDOWN_FRAMES = 4 * 60
MAX_ACTIVE_PICKUPS = 1

def rand_point_in_arena(radius):
    cx = random.randint(ARENA_X + radius, ARENA_X + ARENA_WIDTH - radius)
    cy = random.randint(ARENA_Y + radius, ARENA_Y + ARENA_HEIGHT - radius)
    return cx, cy

def maybe_spawn_pickup():
    global pickup_spawn_cooldown
    if pickup_spawn_cooldown > 0:
        pickup_spawn_cooldown -= 1; return
    if len(pickups) >= MAX_ACTIVE_PICKUPS: return
    if random.random() < 0.015:
        cx, cy = rand_point_in_arena(Pickup.RADIUS)
        kind = random.choice(["health", "inv"])
        pickups.append(HealthPickup(cx, cy) if kind=="health" else InvincibilityPickup(cx, cy))
        pickup_spawn_cooldown = PICKUP_COOLDOWN_FRAMES

def resolve_pickup_collisions():
    global pickups, pickup_flashes
    new_list = []
    for p in pickups:
        hits = p.colliding_fighters(fighter1, fighter2)
        if not hits:
            new_list.append(p); continue
        if len(hits) == 2:
            target = fighter1 if random.random() < 0.5 else fighter2
        elif hits[0] == 1:
            target = fighter1
        else:
            target = fighter2
        
        # Add visual feedback for pickup collection
        if isinstance(p, HealthPickup):
            flash_color = (34, 197, 94)  # green for health
            sound_manager.play_pickup("health")
        elif isinstance(p, InvincibilityPickup):
            flash_color = (255, 255, 255)  # white for invincibility
            sound_manager.play_pickup("invincibility")
        else:
            flash_color = (255, 255, 0)  # yellow for generic pickups
            sound_manager.play_pickup("generic")
            
        # Create expanding ring effect
        pickup_flashes.append((p.cx, p.cy, 20, flash_color))
        
        # Add small screen shake for feedback
        global shake_timer, shake_intensity
        shake_timer = max(shake_timer, 4)
        shake_intensity = max(shake_intensity, 0.5)
        
        p.apply(target)
    pickups = new_list

# === Fighters / match ===
fighter1 = fighter2 = None
f1_exploded = False; f2_exploded = False
player_bet = None  # "RED" or "BLUE"

def random_spawn():
    x = random.randint(ARENA_X, ARENA_X + ARENA_WIDTH - FIGHTER_WIDTH)
    y = random.randint(ARENA_Y, ARENA_Y + ARENA_HEIGHT - FIGHTER_HEIGHT)
    return x, y

def reset_match():
    global fighter1, fighter2, particle_system, damage_texts
    global shake_timer, shake_intensity, shake_offset, blurred_bg_pause
    global result_text, result_color, gameover_menu_index, f1_exploded, f2_exploded
    global go_fade_t, go_menu_alpha, pickups, pickup_spawn_cooldown
    global points_delta, delta_color, delta_count_value

    x1,y1 = random_spawn(); x2,y2 = random_spawn()
    fighter1 = Fighter(x1,y1, dx,dy, FIGHTER_WIDTH,FIGHTER_HEIGHT, (255,0,0), health,
                       ARENA_X,ARENA_Y,ARENA_WIDTH,ARENA_HEIGHT)
    fighter2 = Fighter(x2,y2,-dx,-dy, FIGHTER_WIDTH,FIGHTER_HEIGHT, (0,0,255), health,
                       ARENA_X,ARENA_Y,ARENA_WIDTH,ARENA_HEIGHT)
    fighter1.displayed_health = health; fighter2.displayed_health = health

    # Setup particle system with arena bounds for physics
    particle_system.clear()
    particle_system.set_arena_bounds(ARENA_X, ARENA_Y, ARENA_WIDTH, ARENA_HEIGHT)
    damage_texts = []
    shake_timer = 0; shake_intensity = 1.0; shake_offset = [0,0]
    blurred_bg_pause = None
    result_text = ""; result_color = (255,255,255)
    gameover_menu_index = 0
    f1_exploded = False; f2_exploded = False
    go_fade_t = 0; go_menu_alpha = 0

    # points animation state resets each round
    points_delta = 0
    delta_color = (255,255,255)
    delta_count_value = 0

    pickups = []
    pickup_spawn_cooldown = 2 * 60

def explode_fighter(f, count=55):
    cx = int(f.x + f.width/2); cy = int(f.y + f.height/2)
    # Enhanced explosion with varied particle types
    particle_system.add_explosion(cx, cy, f.base_color, count)

def round_winner():
    red_dead  = fighter1.health <= 0
    blue_dead = fighter2.health <= 0
    if red_dead and blue_dead: return None
    if red_dead:  return "BLUE"
    if blue_dead: return "RED"
    return None

# === Splash screen helpers ===
def draw_splash():
    screen.fill((0,0,0))
    title = font_big.render("HitBox", True, (255,255,255))
    tw, th = title.get_size()
    screen.blit(title, (SCREEN_WIDTH//2 - tw//2, SCREEN_HEIGHT//2 - th - 20))
    t = pygame.time.get_ticks() / 1000.0
    alpha = int(220 * (0.5 + 0.5 * math.sin(2.3 * t)))
    press = font_small.render("Press Enter", True, (255,255,255))
    press.set_alpha(alpha)
    pw, ph = press.get_size()
    screen.blit(press, (SCREEN_WIDTH//2 - pw//2, SCREEN_HEIGHT//2 + 12))

# === Character select layout ===
SELECT_BOX_W, SELECT_BOX_H = 160, 160
SELECT_GAP = 24
total_w = SELECT_BOX_W * 2 + SELECT_GAP
start_x = (SCREEN_WIDTH - total_w) // 2
start_y = 120
RED_BOX_RECT  = pygame.Rect(start_x + SELECT_BOX_W + SELECT_GAP, start_y, SELECT_BOX_W, SELECT_BOX_H)
BLUE_BOX_RECT = pygame.Rect(start_x, start_y, SELECT_BOX_W, SELECT_BOX_H)
click_flash_frames = 0
click_flash_rect = None

def draw_select():
    global click_flash_frames
    screen.fill((0,0,0))
    head = font_select_head.render("WHO WILL WIN?", True, (255,255,255))
    hw, hh = head.get_size()
    screen.blit(head, (SCREEN_WIDTH//2 - hw//2, 40))
    mx, my = pygame.mouse.get_pos()
    hover_red  = RED_BOX_RECT.collidepoint(mx, my)
    hover_blue = BLUE_BOX_RECT.collidepoint(mx, my)
    def draw_choice(rect, color, hover):
        fill_color = (255,255,255) if hover else (0,0,0)
        pygame.draw.rect(screen, fill_color, rect)
        pygame.draw.rect(screen, (255,255,255), rect, 3)
        inner = rect.inflate(-rect.w//3, -rect.h//3)
        pygame.draw.rect(screen, color if not hover else (0,0,0), inner)
    draw_choice(RED_BOX_RECT,  (255,0,0), hover_red)
    draw_choice(BLUE_BOX_RECT, (0,0,255), hover_blue)
    hint = None; color = (255,255,255)
    if hover_red:
        hint = "RED WILL WIN"; color = (255,0,0)
    elif hover_blue:
        hint = "BLUE WILL WIN"; color = (0,0,255)
    if hint:
        txt = font_select_hint.render(hint, True, color)
        tw, th = txt.get_size()
        mid = (RED_BOX_RECT.centerx + BLUE_BOX_RECT.centerx) // 2
        screen.blit(txt, (mid - tw//2, start_y + SELECT_BOX_H + 18))
    if click_flash_frames > 0 and click_flash_rect is not None:
        flash = pygame.Surface((click_flash_rect.w, click_flash_rect.h))
        flash.fill((255,255,255))
        alpha = int(200 * (click_flash_frames / 8))
        flash.set_alpha(alpha)
        screen.blit(flash, (click_flash_rect.x, click_flash_rect.y))
        click_flash_frames -= 1

# === State switching ===
def switch_state(new_state):
    global state
    if new_state == STATE_SELECT:
        pygame.mouse.set_visible(True)
    elif new_state == STATE_PLAYING:
        pygame.mouse.set_visible(False)
        reset_match()
    state = new_state

# === Init ===
reset_match()  # prep assets/state
state = STATE_SPLASH

# === Main Loop ===
running = True
while running:
    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if state == STATE_SPLASH:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    sound_manager.play_menu_select()
                    transition.start(24, STATE_SELECT)

            elif state == STATE_SELECT:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    sound_manager.play_menu_navigate()
                    pygame.mouse.set_pos(RED_BOX_RECT.center)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    sound_manager.play_menu_navigate()
                    pygame.mouse.set_pos(BLUE_BOX_RECT.center)
                elif event.key in (pygame.K_ESCAPE,):
                    sound_manager.play_menu_select()
                    transition.start(24, STATE_SPLASH)
                elif event.key == pygame.K_RETURN:
                    mx, my = pygame.mouse.get_pos()
                    if RED_BOX_RECT.collidepoint(mx, my) or BLUE_BOX_RECT.collidepoint(mx, my):
                        player_bet = "RED" if RED_BOX_RECT.collidepoint(mx, my) else "BLUE"
                        click_flash_rect = RED_BOX_RECT.copy() if player_bet=="RED" else BLUE_BOX_RECT.copy()
                        click_flash_frames = 8
                        sound_manager.play_game_start()
                        transition.start(28, STATE_PLAYING)

            elif state == STATE_PLAYING:
                if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                    state = STATE_PAUSED
                    snap = screen.copy()
                    blurred_bg_pause = fast_blur(snap, scale=0.22, passes=2)
                    pause_menu_index = 0

            elif state == STATE_PAUSED:
                if event.key == pygame.K_RETURN:
                    sound_manager.play_menu_select()
                    choice = ["Resume","Quit"][pause_menu_index]
                    if choice == "Resume":
                        state = STATE_PLAYING; blurred_bg_pause = None
                    else:
                        running = False
                elif event.key in (pygame.K_UP, pygame.K_w):
                    sound_manager.play_menu_navigate()
                    pause_menu_index = (pause_menu_index - 1) % 2
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    sound_manager.play_menu_navigate()
                    pause_menu_index = (pause_menu_index + 1) % 2
                elif event.key == pygame.K_ESCAPE:
                    sound_manager.play_menu_select()
                    state = STATE_PLAYING; blurred_bg_pause = None

            elif state == STATE_GAMEOVER:
                if event.key == pygame.K_RETURN:
                    choice = gameover_menu_items[gameover_menu_index]
                    if choice == "Play Again":
                        transition.start(24, STATE_SELECT)
                    else:
                        running = False
                elif event.key in (pygame.K_UP, pygame.K_w):
                    gameover_menu_index = (gameover_menu_index - 1) % len(gameover_menu_items)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    gameover_menu_index = (gameover_menu_index + 1) % len(gameover_menu_items)

        elif event.type == pygame.MOUSEBUTTONDOWN and state == STATE_SELECT:
            mx, my = pygame.mouse.get_pos()
            if RED_BOX_RECT.collidepoint(mx, my) or BLUE_BOX_RECT.collidepoint(mx, my):
                player_bet = "RED" if RED_BOX_RECT.collidepoint(mx, my) else "BLUE"
                click_flash_rect = RED_BOX_RECT.copy() if player_bet=="RED" else BLUE_BOX_RECT.copy()
                click_flash_frames = 8
                transition.start(28, STATE_PLAYING)

    # === UPDATE ===
    if state in (STATE_PLAYING, STATE_GAMEOVER_TRANS, STATE_GAMEOVER):
        fighter1.move(); fighter2.move()
        fighter1.update_effects(); fighter2.update_effects()
        update_health_bar_value(fighter1); update_health_bar_value(fighter2)

        if shake_timer > 0:
            # Dynamic shake based on intensity
            max_shake = int(8 * shake_intensity)
            shake_offset[0] = random.randint(-max_shake, max_shake)
            shake_offset[1] = random.randint(-max_shake, max_shake)
            shake_timer -= 1
            # Intensity decreases over time for natural feel
            shake_intensity *= 0.9
        else:
            shake_offset = [0, 0]
            shake_intensity = 1.0

        # Pickups
        if state == STATE_PLAYING:
            maybe_spawn_pickup()
            for pk in pickups: pk.update()
            pickups[:] = [pk for pk in pickups if not pk.dead]
            resolve_pickup_collisions()
        else:
            for pk in pickups: pk.update()
            pickups[:] = [pk for pk in pickups if not pk.dead]

        # Enhanced Collisions with better visual feedback
        if state == STATE_PLAYING and fighter1.collides_with(fighter2):
            fighter1.dx *= -1; fighter1.dy *= -1
            fighter2.dx *= -1; fighter2.dy *= -1

            dmg1 = fighter1.take_damage(DAMAGE)
            dmg2 = fighter2.take_damage(DAMAGE)

            if (dmg1 > 0) or (dmg2 > 0):
                # Dynamic shake intensity based on total damage dealt
                total_damage = dmg1 + dmg2
                shake_timer = 8 + min(12, total_damage // 5)  # longer shake for more damage
                shake_intensity = 1.0 + (total_damage / 20.0)  # stronger shake for more damage
                
                # Play collision sound with intensity
                sound_manager.play_collision(shake_intensity)
                
                overlap = fighter1.get_rect().clip(fighter2.get_rect())
                if overlap.width > 0 and overlap.height > 0:
                    cx, cy = overlap.center
                    # Enhanced collision effects
                    particle_system.add_collision_sparks(cx, cy, 12)
                    particle_system.add_explosion(cx, cy, (255, 255, 255), 8)
                    
                if dmg1 > 0:
                    damage_texts.append(DamageText(fighter1.x+fighter1.width/2, fighter1.y-6, dmg1, (255,120,120)))
                    # Add damage sparks around fighter1
                    particle_system.add_damage_sparks(fighter1.x+fighter1.width/2, fighter1.y+fighter1.height/2, (255,120,120))
                if dmg2 > 0:
                    damage_texts.append(DamageText(fighter2.x+fighter2.width/2, fighter2.y-6, dmg2, (120,170,255)))
                    # Add damage sparks around fighter2
                    particle_system.add_damage_sparks(fighter2.x+fighter2.width/2, fighter2.y+fighter2.height/2, (120,170,255))

        # Update particle system and damage texts
        particle_system.update()
        for dt in damage_texts: dt.update()
        damage_texts = [dt for dt in damage_texts if not dt.dead]
        
        # Update pickup flashes
        pickup_flashes = [(x, y, timer-1, color) for x, y, timer, color in pickup_flashes if timer > 0]

        # deaths -> transition to GAMEOVER with scoring prep
        if state == STATE_PLAYING:
            if fighter1.health <= 0 and not f1_exploded:
                sound_manager.play_explosion()
                explode_fighter(fighter1); f1_exploded = True
            if fighter2.health <= 0 and not f2_exploded:
                sound_manager.play_explosion()
                explode_fighter(fighter2); f2_exploded = True
            if (fighter1.health <= 0) or (fighter2.health <= 0):
                win = round_winner()
                # compute text relative to player's bet
                bet_color = (255,0,0) if player_bet == "RED" else (0,0,255)
                result_color = bet_color
                if win is None:
                    result_text = "DRAW"
                    points_delta = 0
                    delta_color = (255,255,255)  # white
                else:
                    if win == player_bet:
                        result_text = "YOU WON"
                        points_delta = POINT_WIN
                        delta_color = (255,255,0)  # yellow for gain
                    else:
                        result_text = "YOU LOST"
                        points_delta = POINT_LOSS
                        delta_color = (255,255,255)  # white for loss
                delta_count_value = 0
                state = STATE_GAMEOVER_TRANS
                go_fade_t = 0
                go_menu_alpha = 0

        # Gameover transition: animate blur/fade and the point counter
        if state == STATE_GAMEOVER_TRANS:
            go_fade_t += 1
            # animate the count up/down to |delta|
            total = abs(points_delta)
            delta_count_value = int(total * (go_fade_t / GO_FADE_FRAMES))
            if go_fade_t >= GO_FADE_FRAMES:
                # apply the points AFTER the count finishes
                current_score = max(0, current_score + points_delta)
                if current_score > high_score:
                    high_score = current_score
                # If score hits 0, boot back to Start (keep high score, reset score)
                if current_score <= 0:
                    current_score = 100  # new run
                    player_bet = None
                    transition.start(24, STATE_SPLASH)
                else:
                    state = STATE_GAMEOVER
                    go_menu_alpha = 0

        if state == STATE_GAMEOVER:
            go_menu_alpha = min(255, go_menu_alpha + 18)

    # transition tick (runs regardless of state)
    transition.update()

    # === DRAW ===
    if state == STATE_SPLASH:
        draw_splash()
        draw_scoreboard(show_high=False)  # only SCORE on Start

    elif state == STATE_SELECT:
        draw_select()
        draw_scoreboard(show_high=True)

    else:
        # gameplay-style frame
        screen.fill("black")
        pygame.draw.rect(screen, "white",
            (ARENA_X-OUTLINE_THICKNESS+shake_offset[0],
             ARENA_Y-OUTLINE_THICKNESS+shake_offset[1],
             ARENA_WIDTH+2*OUTLINE_THICKNESS,
             ARENA_HEIGHT+2*OUTLINE_THICKNESS))
        pygame.draw.rect(screen, "black",
            (ARENA_X+shake_offset[0], ARENA_Y+shake_offset[1], ARENA_WIDTH, ARENA_HEIGHT))

        if fighter1 and fighter1.health > 0: fighter1.draw(screen, shake_offset)
        if fighter2 and fighter2.health > 0: fighter2.draw(screen, shake_offset)

        for pk in pickups: pk.draw(screen, shake_offset)
        
        # Draw enhanced particle system
        particle_system.draw(screen, shake_offset)
        
        # Draw pickup collection flashes
        draw_pickup_flashes(screen, shake_offset)
        
        for dt in damage_texts: dt.draw(screen, shake_offset)

        # HUD
        if fighter1 and fighter2:
            draw_health_bar(screen, BLUE_BAR_X, BLUE_BAR_Y,
                fighter2.health, fighter2.displayed_health, 100, (0,0,255), shake_offset, align="left")
            draw_health_bar(screen, RED_BAR_X, RED_BAR_Y,
                fighter1.health, fighter1.displayed_health, 100, (255,0,0), shake_offset, align="right")
            draw_centered_label("BLUE", BLUE_BAR_X, BLUE_BAR_Y, HEALTH_BAR_WIDTH, (150,180,255), shake_offset)
            draw_centered_label("RED",  RED_BAR_X,  RED_BAR_Y,  HEALTH_BAR_WIDTH, (255,160,160), shake_offset)

        # Overlays
        if state == STATE_PAUSED:
            if blurred_bg_pause is None:
                snap = screen.copy()
                blurred_bg_pause = fast_blur(snap, scale=0.22, passes=2)
            draw_pause_menu(screen, blurred_bg_pause, pause_menu_items, pause_menu_index)
            draw_scoreboard(show_high=True)

        elif state in (STATE_GAMEOVER_TRANS, STATE_GAMEOVER):
            progress = 1.0 if state == STATE_GAMEOVER else (go_fade_t / GO_FADE_FRAMES)
            draw_gameover_overlay(screen, progress, show_menu=(state == STATE_GAMEOVER), menu_alpha=go_menu_alpha)
            draw_scoreboard(show_high=True)

        else:
            # STATE_PLAYING
            draw_scoreboard(show_high=True)

    # draw transition overlay last
    transition.draw_overlay(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()