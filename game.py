# =============================================================================
#  game.py — Game manager: states, rendering, event handling
# =============================================================================
import math, pygame, random
from grid    import Grid
from player  import Player
from monster import Monster
from level_data import generate_level_grid, PLAYER_STARTS, MONSTER_STARTS
from constants  import *


# ── Font cache (initialised in GameManager.__init__) ─────────────────────────
_fonts: dict = {}

def _font(size: int, bold=False) -> pygame.font.Font:
    key = (size, bold)
    if key not in _fonts:
        try:
            _fonts[key] = pygame.font.SysFont('Segoe UI', size, bold=bold)
        except Exception:
            _fonts[key] = pygame.font.Font(None, size)
    return _fonts[key]


# ── Drawing helpers ───────────────────────────────────────────────────────────
def _text(surf, txt, size, colour, pos, bold=False, anchor='topleft'):
    f = _font(size, bold)
    s = f.render(str(txt), True, colour)
    r = s.get_rect(**{anchor: pos})
    surf.blit(s, r)
    return r

def _progress_bar(surf, rect, pct, fg, bg=(25, 30, 70), border=(50, 70, 160)):
    pygame.draw.rect(surf, bg,     rect, border_radius=6)
    if pct > 0:
        inner = pygame.Rect(rect.x + 2, rect.y + 2,
                            int((rect.w - 4) * pct / 100), rect.h - 4)
        if inner.w > 0:
            pygame.draw.rect(surf, fg, inner, border_radius=4)
    pygame.draw.rect(surf, border, rect, 2, border_radius=6)


# ── Cell rendering ────────────────────────────────────────────────────────────
def _draw_cell(surf, r, c, cell_type, is_traversed, time_ms):
    x = c * CELL_SIZE
    y = HEADER_H + r * CELL_SIZE
    rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

    if cell_type == WALL:
        # Wood plank texture
        pygame.draw.rect(surf, C_WALL, rect)
        pygame.draw.rect(surf, C_WALL_EDGE, rect, 2)
        pygame.draw.line(surf, C_WALL_INNER, (x + 5, y + 5), (x + 5, y + CELL_SIZE - 5), 2)
        pygame.draw.line(surf, C_WALL_INNER, (x + CELL_SIZE - 5, y + 5), (x + CELL_SIZE - 5, y + CELL_SIZE - 5), 2)
        pygame.draw.line(surf, C_WALL_INNER, (x + 10, y + CELL_SIZE // 2), (x + 20, y + CELL_SIZE // 2), 1)
        return

    bg = C_TRAVERSED if is_traversed else C_EMPTY
    pygame.draw.rect(surf, bg, rect)
    
    # Subtle parchment map circles
    if not is_traversed:
        pygame.draw.circle(surf, (25, 20, 15), (x + CELL_SIZE//2, y + CELL_SIZE//2), CELL_SIZE//2 - 2, 1)

    if cell_type == EMPTY and not is_traversed:
        cx, cy = x + CELL_SIZE // 2, y + CELL_SIZE // 2
        # Glowing gold coin
        pulse = 1 + int(2 * abs(math.sin(time_ms / 200 + r + c)))
        s = pygame.Surface((10 + pulse*2, 10 + pulse*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 200, 0, 80), (5 + pulse, 5 + pulse), 3 + pulse)
        surf.blit(s, (cx - 5 - pulse, cy - 5 - pulse))
        pygame.draw.circle(surf, C_DOT, (cx, cy), 3)
        pygame.draw.circle(surf, (255, 255, 200), (cx - 1, cy - 1), 1) # Coin shine

def _draw_item(surf, r, c, item_type, time_ms):
    x = c * CELL_SIZE
    y = HEADER_H + r * CELL_SIZE
    rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

    if item_type == TAR:
        pygame.draw.rect(surf, C_TAR, rect)
        pygame.draw.rect(surf, C_TAR_BORDER, rect, 2)
        for ox, oy in [(-5, -4), (4, 2), (-3, 5), (5, -5)]:
            pygame.draw.circle(surf, C_TAR_BORDER,
                               (x + CELL_SIZE//2 + ox, y + CELL_SIZE//2 + oy), 3)

    elif item_type == SPEED:
        pygame.draw.rect(surf, C_SPEED, rect)
        pygame.draw.rect(surf, C_SPEED_BORDER, rect, 2)
        cx, cy = x + CELL_SIZE//2, y + CELL_SIZE//2
        pts = [(cx - 8, cy), (cx + 2, cy - 6), (cx + 2, cy - 2),
               (cx + 8, cy - 2), (cx + 8, cy + 2), (cx + 2, cy + 2), (cx + 2, cy + 6)]
        pygame.draw.polygon(surf, C_SPEED_BORDER, pts)

    elif item_type == STEALTH:
        pygame.draw.rect(surf, C_STEALTH, rect)
        pygame.draw.rect(surf, C_STEALTH_BORDER, rect, 2)
        # Eye icon with a slash
        cx, cy = x + CELL_SIZE // 2, y + CELL_SIZE // 2
        pygame.draw.ellipse(surf, C_STEALTH_BORDER, (cx - 8, cy - 4, 16, 8), 1)
        pygame.draw.line(surf, C_STEALTH_BORDER, (cx - 8, cy - 6), (cx + 8, cy + 6), 2)

    elif item_type == FROST:
        pygame.draw.rect(surf, C_FROST, rect)
        pygame.draw.rect(surf, C_FROST_BORDER, rect, 2)
        cx, cy = x + CELL_SIZE // 2, y + CELL_SIZE // 2
        for angle in [0, 45, 90, 135]:
            rad = math.radians(angle)
            dx, dy = int(8 * math.cos(rad)), int(8 * math.sin(rad))
            pygame.draw.line(surf, C_FROST_BORDER,
                             (cx - dx, cy - dy), (cx + dx, cy + dy), 2)
                             
    elif item_type == FIRE:
        pygame.draw.rect(surf, C_FIRE, rect)
        pygame.draw.rect(surf, C_FIRE_BORDER, rect, 2)
        cx, cy = x + CELL_SIZE // 2, y + CELL_SIZE // 2
        pts = [(cx, cy - 8), (cx + 6, cy + 2), (cx + 3, cy + 8), (cx - 3, cy + 8), (cx - 6, cy + 2)]
        pygame.draw.polygon(surf, C_FIRE_BORDER, pts)


# ── Player rendering ──────────────────────────────────────────────────────────
def _draw_player(surf, player: Player, time_ms: int):
    px, py = player.get_render_pos()
    r = CELL_SIZE // 2 - 2

    # Pick colour based on active effect
    eff, timer = player.get_effect_info()
    if player.frozen:
        body_col   = C_PLAYER_FROZEN
        outline_col = C_FROST_BORDER
    elif eff == 'tar':
        body_col   = C_PLAYER_TAR
        outline_col = C_TAR_BORDER
    elif eff == 'speed':
        # Speed lines (blue trail)
        body_col   = C_PLAYER_SPEED
        outline_col = C_SPEED_BORDER
        for i in range(1, 4):
            alpha = 180 - i * 45
            dc, dr = player.curr_dir
            tx = px - dc * i * 6
            ty = py - dr * i * 6
            s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*C_PLAYER_SPEED, alpha), (r, r), max(1, r - i * 2))
            surf.blit(s, (tx - r, ty - r))
    elif eff == 'stealth':
        body_col   = C_PLAYER_STEALTH
        outline_col = C_STEALTH_BORDER
    elif eff == 'fire':
        body_col   = C_PLAYER_FIRE
        outline_col = C_FIRE_BORDER
    else:
        body_col   = C_PLAYER
        outline_col = C_PLAYER_OUTLINE

    # Pulsing glow for freeze and fire
    if player.frozen:
        pulse = 3 + int(2 * abs(math.sin(time_ms / 200)))
        s = pygame.Surface(((r + pulse) * 2, (r + pulse) * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*C_FROST_BORDER, 80), (r + pulse, r + pulse), r + pulse)
        surf.blit(s, (px - r - pulse, py - r - pulse))
    elif eff == 'fire':
        pulse = 4 + int(3 * abs(math.sin(time_ms / 150)))
        s = pygame.Surface(((r + pulse) * 2, (r + pulse) * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*C_FIRE_BORDER, 100), (r + pulse, r + pulse), r + pulse)
        surf.blit(s, (px - r - pulse, py - r - pulse))

    # --- CHANGED: Jack Sparrow Pirate ---
    is_moving = player.moving
    swing = math.sin(time_ms / 100) * 8 if is_moving else 0
    
    # Create temporary surface
    s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    cx, cy = CELL_SIZE // 2, CELL_SIZE // 2
    
    # Body (Brown Trench Coat)
    body_y = cy - 2 + abs(swing) * 0.3
    pygame.draw.rect(s, (80, 50, 30), (cx - 6, body_y, 12, 10), border_radius=2)
    # Belt (Red sash)
    pygame.draw.rect(s, (150, 30, 30), (cx - 6, body_y + 8, 12, 3))
    
    # Legs (Brown pants/boots)
    leg_l = body_y + 11 + swing
    leg_r = body_y + 11 - swing
    pygame.draw.line(s, (50, 40, 30), (cx - 3, body_y + 10), (cx - 3, leg_l), 4)
    pygame.draw.line(s, (50, 40, 30), (cx + 3, body_y + 10), (cx + 3, leg_r), 4)
    
    # Arms (White shirt / Brown coat sleeves)
    pygame.draw.line(s, (80, 50, 30), (cx - 6, body_y + 2), (cx - 8, body_y + 6 - swing), 3)
    # Right arm holding a sword
    sword_y = body_y + 6 + swing
    pygame.draw.line(s, (80, 50, 30), (cx + 6, body_y + 2), (cx + 8, sword_y), 3)
    # Sword
    pygame.draw.line(s, (200, 200, 200), (cx + 8, sword_y), (cx + 8, sword_y - 8), 2)
    pygame.draw.line(s, (255, 215, 0), (cx + 6, sword_y), (cx + 10, sword_y), 2) # hilt
    
    # Head
    pygame.draw.circle(s, (220, 180, 140), (cx, body_y - 4), 5)
    
    # Dreads (Black/Dark brown lines)
    pygame.draw.line(s, (30, 20, 10), (cx - 4, body_y - 4), (cx - 6, body_y + 2), 2)
    pygame.draw.line(s, (30, 20, 10), (cx + 4, body_y - 4), (cx + 6, body_y + 2), 2)
    
    # Red Bandana
    pygame.draw.line(s, (180, 30, 30), (cx - 5, body_y - 6), (cx + 5, body_y - 6), 3)
    
    # Tricorne Hat
    pts = [(cx - 8, body_y - 5), (cx + 8, body_y - 5), (cx, body_y - 12)]
    pygame.draw.polygon(s, (40, 30, 20), pts)
    
    # Rotate surface based on direction
    dc, dr = player.curr_dir
    angle = 0
    if dr == -1: angle = 0
    elif dr == 1: angle = 180
    elif dc == -1: angle = 90
    elif dc == 1: angle = -90
    
    rotated = pygame.transform.rotate(s, angle)
    rect = rotated.get_rect(center=(px, py))
    surf.blit(rotated, rect.topleft)
    
    # Effects (Frozen/Fire/Tar/Speed)
    if player.frozen:
        pygame.draw.circle(surf, C_FROST_BORDER, (px, py), r + 2, 2)
    elif eff == 'fire':
        pygame.draw.circle(surf, C_FIRE_BORDER, (px, py), r + 2, 2)
    elif eff == 'tar':
        pygame.draw.circle(surf, C_TAR_BORDER, (px, py), r + 2, 2)


def _draw_monster(surf, monster: Monster, time_ms: int):
    px, py = monster.get_render_pos()
    colour = MONSTER_COLORS[monster.idx]
    r = CELL_SIZE // 2 - 2

    # Draw effect indicators
    if monster.frozen:
        colour = C_FROST_BORDER
    elif monster.effect == 'tar':
        colour = C_TAR_BORDER
    elif monster.effect == 'speed':
        colour = C_SPEED_BORDER
    elif monster.effect == 'stealth':
        colour = C_STEALTH_BORDER

    top = py - r

    # --- CHANGED: POTC Monsters ---
    bob = math.sin(time_ms / 150 + monster.idx) * 3
    my = py + bob
    
    if monster.idx % 4 == 0:
        # Skeleton Pirate
        pygame.draw.circle(surf, (220, 220, 220), (px, my), r)
        pygame.draw.circle(surf, (20, 20, 20), (px - 3, my - 2), 2)
        pygame.draw.circle(surf, (20, 20, 20), (px + 3, my - 2), 2)
        pygame.draw.rect(surf, (220, 220, 220), (px - 4, my + r - 4, 8, 4))
        pygame.draw.line(surf, (50, 50, 50), (px - 2, my + r - 4), (px - 2, my + r))
        pygame.draw.line(surf, (50, 50, 50), (px + 2, my + r - 4), (px + 2, my + r))
        pygame.draw.line(surf, (200, 50, 50), (px - r, my - r + 3), (px + r, my - r + 3), 4)

    elif monster.idx % 4 == 1:
        # Davy Jones (Octopus face)
        pygame.draw.circle(surf, (60, 150, 120), (px, my), r)
        for tx in [-4, -1, 2, 5]:
            twiggle = math.sin(time_ms / 100 + tx) * 2
            pygame.draw.line(surf, (40, 130, 100), (px + tx, my), (px + tx + twiggle, my + r + 4), 2)
        pygame.draw.circle(surf, (255, 255, 0), (px - 4, my - 2), 2)
        pygame.draw.circle(surf, (255, 255, 0), (px + 4, my - 2), 2)

    elif monster.idx % 4 == 2:
        # Ghost Pirate
        pulse_alpha = 100 + int(50 * math.sin(time_ms / 100))
        s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (100, 200, 255, pulse_alpha), (r, r), r)
        pygame.draw.circle(s, (50, 100, 255, pulse_alpha), (r, r), r, 2)
        pygame.draw.circle(s, (0, 0, 0, 150), (r - 4, r - 2), 3)
        pygame.draw.circle(s, (0, 0, 0, 150), (r + 4, r - 2), 3)
        pygame.draw.rect(s, (50, 70, 100, pulse_alpha), (r - 10, r - 10, 20, 6))
        surf.blit(s, (px - r, my - r))

    else:
        # Kraken Tentacle
        pygame.draw.ellipse(surf, (20, 10, 30), (px - r, my + r - 4, r*2, 6))
        twiggle = math.sin(time_ms / 80) * 4
        pts = [(px - 6, my + r), (px - 2 + twiggle, my - r), (px + 2 + twiggle, my - r), (px + 6, my + r)]
        pygame.draw.polygon(surf, (150, 50, 150), pts)
        pygame.draw.circle(surf, (200, 100, 200), (px - 3 + int(twiggle*0.5), my), 2)
        pygame.draw.circle(surf, (200, 100, 200), (px - 4 + int(twiggle*0.8), my - 6), 2)


# ── Sidebar rendering ─────────────────────────────────────────────────────────
def _draw_sidebar(surf, game, time_ms: int):
    x0 = GAME_AREA_W
    rect = pygame.Rect(x0, 0, SIDEBAR_W, SCREEN_H)
    pygame.draw.rect(surf, C_SIDEBAR_BG, rect)
    pygame.draw.line(surf, C_SIDEBAR_LINE, (x0, 0), (x0, SCREEN_H), 2)

    y = 12
    cx = x0 + SIDEBAR_W // 2

    # ── SCORE ─────────────────────────────────────────────────────────────────
    _text(surf, 'SCORE', 13, C_TEXT_SECONDARY, (cx, y), anchor='midtop')
    y += 18
    _text(surf, f'{game.score:,}', 28, C_TEXT_GOLD, (cx, y), bold=True, anchor='midtop')
    y += 36

    pygame.draw.line(surf, C_SIDEBAR_LINE, (x0 + 10, y), (x0 + SIDEBAR_W - 10, y), 1)
    y += 8

    # ── LEVEL / LIVES ─────────────────────────────────────────────────────────
    _text(surf, f'LEVEL  {game.level} / {MAX_LEVELS}', 14, C_TEXT_PRIMARY,
          (cx, y), bold=True, anchor='midtop')
    y += 20
    hearts = '♥ ' * game.lives + '♡ ' * max(0, LIVES - game.lives)
    _text(surf, hearts.strip(), 16, (220, 60, 80), (cx, y), anchor='midtop')
    y += 26

    pygame.draw.line(surf, C_SIDEBAR_LINE, (x0 + 10, y), (x0 + SIDEBAR_W - 10, y), 1)
    y += 10

    # ── PROGRESS ──────────────────────────────────────────────────────────────
    _text(surf, 'COVERAGE', 13, C_TEXT_SECONDARY, (cx, y), anchor='midtop')
    y += 18
    pct = game.grid.traversal_pct() if game.grid else 0.0
    _progress_bar(surf, pygame.Rect(x0 + 12, y, SIDEBAR_W - 24, 14), pct,
                  fg=C_TEXT_GREEN)
    y += 18
    _text(surf, f'{pct:.1f}%', 13, C_TEXT_GREEN, (cx, y), anchor='midtop')
    y += 24

    pygame.draw.line(surf, C_SIDEBAR_LINE, (x0 + 10, y), (x0 + SIDEBAR_W - 10, y), 1)
    y += 10

    # ── ACTIVE EFFECT ─────────────────────────────────────────────────────────
    _text(surf, 'ACTIVE EFFECT', 13, C_TEXT_SECONDARY, (cx, y), anchor='midtop')
    y += 18

    if game.player:
        eff, timer = game.player.get_effect_info()
        if game.player.frozen:
            eff_name = '❄  FROZEN'
            col = C_FROST_BORDER
        elif eff == 'tar':
            eff_name = '⬛ TAR (slow)'
            col = C_TAR_BORDER
        elif eff == 'speed':
            eff_name = '💨 SPEED (fast)'
            col = C_SPEED_BORDER
        elif eff == 'stealth':
            eff_name = '👁 STEALTH (hidden)'
            col = C_STEALTH_BORDER
        elif eff == 'fire':
            eff_name = '🔥 FIRE (kill ghosts)'
            col = C_FIRE_BORDER
        else:
            eff_name = '— none —'
            col = C_TEXT_SECONDARY

        _text(surf, eff_name, 13, col, (cx, y), anchor='midtop')
        y += 16
        if eff or game.player.frozen:
            bar_pct = (timer / {
                'tar': TAR_DUR, 'speed': SPEED_DUR,
                'stealth': STEALTH_DUR, 'fire': FIRE_DUR, 'frost': FROST_DUR
            }.get(eff or 'frost', 1)) * 100
            _progress_bar(surf, pygame.Rect(x0 + 12, y, SIDEBAR_W - 24, 8),
                          bar_pct, fg=col)
        y += 16
    else:
        y += 32

    pygame.draw.line(surf, C_SIDEBAR_LINE, (x0 + 10, y), (x0 + SIDEBAR_W - 10, y), 1)
    y += 10

    # ── MONSTERS ──────────────────────────────────────────────────────────────
    _text(surf, 'MONSTERS', 13, C_TEXT_SECONDARY, (cx, y), anchor='midtop')
    y += 18

    if game.monsters:
        for m in game.monsters:
            col = MONSTER_COLORS[m.idx]
            pygame.draw.circle(surf, col, (x0 + 18, y + 7), 6)
            _text(surf, MONSTER_NAMES[m.idx], 13, col, (x0 + 30, y))
            algo_label = ALGO_DISPLAY.get(m.algorithm, m.algorithm)
            _text(surf, algo_label, 11, C_TEXT_SECONDARY, (x0 + 30, y + 15))
            y += 34
    y += 4

    pygame.draw.line(surf, C_SIDEBAR_LINE, (x0 + 10, y), (x0 + SIDEBAR_W - 10, y), 1)
    y += 10

    # ── CONTROLS ──────────────────────────────────────────────────────────────
    _text(surf, 'CONTROLS', 13, C_TEXT_SECONDARY, (cx, y), anchor='midtop')
    y += 18
    for line in ['↑↓←→  Move', 'P       Pause', 'ESC   Menu']:
        _text(surf, line, 12, C_TEXT_SECONDARY, (x0 + 14, y))
        y += 15


# ── Header rendering ──────────────────────────────────────────────────────────
def _draw_header(surf, game, time_ms):
    pygame.draw.rect(surf, C_HEADER_BG, (0, 0, GAME_AREA_W, HEADER_H))
    pygame.draw.line(surf, C_SIDEBAR_LINE, (0, HEADER_H - 1), (GAME_AREA_W, HEADER_H - 1), 2)

    # Pulsing title
    pulse = 0.5 + 0.5 * math.sin(time_ms / 600)
    title_col = tuple(int(a + (b - a) * pulse) for a, b in
                      zip(C_TEXT_GOLD, C_PLAYER_SPEED))
    _text(surf, 'ESCAPE X', 26, title_col, (20, HEADER_H // 2), bold=True, anchor='midleft')

    # Progress hint
    if game.grid:
        pct = game.grid.traversal_pct()
        hint = f'Cover 100% to Escape!  [{pct:.1f}% done]'
        _text(surf, hint, 13, C_TEXT_SECONDARY, (GAME_AREA_W // 2, HEADER_H // 2),
              anchor='center')


# ── Overlay screens ───────────────────────────────────────────────────────────
def _overlay(surf, title, subtitle, colour, hint='Press ENTER to continue'):
    s = pygame.Surface((GAME_AREA_W, SCREEN_H - HEADER_H), pygame.SRCALPHA)
    s.fill((0, 0, 0, 160))
    surf.blit(s, (0, HEADER_H))
    mid_x, mid_y = GAME_AREA_W // 2, SCREEN_H // 2
    _text(surf, title,    40, colour,         (mid_x, mid_y - 40), bold=True, anchor='center')
    _text(surf, subtitle, 18, C_TEXT_PRIMARY, (mid_x, mid_y + 10), anchor='center')
    _text(surf, hint,     14, C_TEXT_SECONDARY,(mid_x, mid_y + 50), anchor='center')


# =============================================================================
#  GameManager
# =============================================================================
class GameManager:
    """
    Owns the game state machine, all entities, and the render loop.

    States:  ST_MENU → ST_PLAYING ↔ ST_PAUSED
                                 → ST_LVLDONE → ST_PLAYING (next level)
                                 → ST_GAMEOVER
             ST_PLAYING → ST_WIN (all levels cleared)
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.clock  = pygame.time.Clock()
        self.running = True

        self.state  = ST_MENU
        self.level  = 1
        self.score  = 0
        self.lives  = LIVES

        self.grid:    Grid    = None
        self.player:  Player  = None
        self.monsters: list   = []

        # Dynamic Item System
        self.active_items = {}       # (r, c) -> {'type': int, 'timer': float}
        self.item_spawn_timer = ITEM_SPAWN_INTERVAL

        # Overlay timing
        self._overlay_timer = 0.0   # seconds to auto-dismiss overlays

        # Flash effect on death
        self._flash = 0.0

        # Particle System
        self.particles = []

    def spawn_particles(self, x, y, col, count=10, speed=50):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            s = random.uniform(speed*0.5, speed)
            self.particles.append({
                'x': x, 'y': y,
                'vx': math.cos(angle) * s, 'vy': math.sin(angle) * s,
                'life': random.uniform(0.2, 0.6),
                'max_life': 0.6,
                'col': col, 'size': random.uniform(1, 3)
            })

        # Audio
        self.sounds = {}
        try:
            self.sounds['move'] = pygame.mixer.Sound('assets/sounds/move.wav')
            self.sounds['move'].set_volume(0.2)
            self.sounds['powerup'] = pygame.mixer.Sound('assets/sounds/powerup.wav')
            self.sounds['powerup'].set_volume(0.5)
            self.sounds['caught'] = pygame.mixer.Sound('assets/sounds/caught.wav')
            self.sounds['caught'].set_volume(0.6)
            self.sounds['kill'] = pygame.mixer.Sound('assets/sounds/kill.wav')
            self.sounds['kill'].set_volume(0.6)
            self.sounds['win'] = pygame.mixer.Sound('assets/sounds/win.wav')
            self.sounds['win'].set_volume(0.6)
            self.sounds['game_over'] = pygame.mixer.Sound('assets/sounds/game_over.wav')
            self.sounds['game_over'].set_volume(0.7)
        except Exception as e:
            print(f"Warning: Could not load sounds: {e}")

    def play_sound(self, name):
        if name in self.sounds:
            self.sounds[name].play()

    # ── Public entry point ────────────────────────────────────────────────────
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self._handle_events()
            self._update(dt)
            self._render()

    # ── Event handling ────────────────────────────────────────────────────────
    def _handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.running = False

            elif ev.type == pygame.KEYDOWN:
                self._on_key(ev.key)

    def _on_key(self, key):
        if self.state == ST_MENU:
            if key == pygame.K_RETURN or key == pygame.K_SPACE:
                self._start_level(1)

        elif self.state == ST_PLAYING:
            if key == pygame.K_UP    or key == pygame.K_w:
                self.player.set_direction(0, -1)
            elif key == pygame.K_DOWN  or key == pygame.K_s:
                self.player.set_direction(0,  1)
            elif key == pygame.K_LEFT  or key == pygame.K_a:
                self.player.set_direction(-1, 0)
            elif key == pygame.K_RIGHT or key == pygame.K_d:
                self.player.set_direction( 1, 0)
            elif key == pygame.K_p:
                self.state = ST_PAUSED
            elif key == pygame.K_ESCAPE:
                self.state = ST_MENU

        elif self.state == ST_PAUSED:
            if key == pygame.K_p or key == pygame.K_ESCAPE:
                self.state = ST_PLAYING

        elif self.state in (ST_LVLDONE, ST_GAMEOVER, ST_WIN):
            if key == pygame.K_RETURN or key == pygame.K_SPACE:
                if self.state == ST_LVLDONE:
                    self._start_level(self.level + 1)
                else:
                    self._reset_game()

    # ── Level initialisation ──────────────────────────────────────────────────
    def _start_level(self, lvl: int):
        if lvl > MAX_LEVELS:
            self.state = ST_WIN
            return
        self.level = lvl
        idx = lvl - 1

        # Build grid (procedurally generate a new maze for this level)
        self.grid = Grid(generate_level_grid(idx))

        # Player
        pr, pc = PLAYER_STARTS[idx]
        self.player = Player(pr, pc)
        self.grid.mark_traversed(pr, pc)

        # Pre-mark the ghost house interior and exit as traversed (no dots)
        for c in range(8, 13):
            self.grid.mark_traversed(9, c)
        self.grid.mark_traversed(10, 10)

        # Monsters
        algos = LEVEL_CONFIGS[idx]
        speed = MONSTER_SPEEDS[idx]
        self.monsters = []
        for i, (mr, mc) in enumerate(MONSTER_STARTS[idx]):
            m = Monster(i, mr, mc, speed, algos[i])
            self.monsters.append(m)

        self.active_items.clear()
        self.item_spawn_timer = ITEM_SPAWN_INTERVAL

        self.state = ST_PLAYING
        self._flash = 0.0

    def _reset_game(self):
        self.score = 0
        self.lives = LIVES
        self.state = ST_MENU

    # ── Update ────────────────────────────────────────────────────────────────
    def _update(self, dt: float):
        if self.state != ST_PLAYING:
            return

        # ── Items ─────────────────────────────────────────────────────────────
        self.item_spawn_timer -= dt
        if self.item_spawn_timer <= 0:
            self.item_spawn_timer = ITEM_SPAWN_INTERVAL
            if len(self.active_items) < MAX_ITEMS:
                empty_cells = []
                for r in range(GRID_ROWS):
                    for c in range(GRID_COLS):
                        if self.grid.get(r, c) == EMPTY and (r, c) not in self.active_items:
                            empty_cells.append((r, c))
                if empty_cells:
                    pos = random.choice(empty_cells)
                    types = [TAR, SPEED, STEALTH, FROST, FIRE]
                    self.active_items[pos] = {'type': random.choice(types), 'timer': ITEM_DESPAWN_TIME}
        
        expired = []
        for pos, data in self.active_items.items():
            data['timer'] -= dt
            if data['timer'] <= 0:
                expired.append(pos)
        for p in expired:
            del self.active_items[p]

        # ── Entities ──────────────────────────────────────────────────────────
        if self.player.update(dt, self.grid):
            self.play_sound('move')

        player_pos = self.player.get_grid_pos()
        player_invisible = self.player.invisible
        for m in self.monsters:
            m.update(dt, self.grid, player_pos, player_invisible)

        # ── Item Consumption ──────────────────────────────────────────────────
        def _check_item(entity):
            pos = entity.get_grid_pos()
            if pos in self.active_items:
                item_type = self.active_items[pos]['type']
                if entity != self.player and item_type == FIRE:
                    return # Monsters cannot eat fire
                item = self.active_items.pop(pos)
                entity.apply_effect(item['type'])
                if entity == self.player:
                    self.play_sound('powerup')
                    px, py = self.player.get_render_pos()
                    self.spawn_particles(px, py, (255, 255, 0), count=15, speed=100)

        _check_item(self.player)
        for m in self.monsters:
            _check_item(m)

        # ── Collision detection ───────────────────────────────────────────────
        for m in self.monsters:
            if self.player.collides_with(m):
                if self.player.effect == 'fire':
                    self.play_sound('kill')
                    self.score += SCORE_KILL_GHOST
                    self.spawn_particles(m.px, m.py, MONSTER_COLORS[m.idx % len(MONSTER_COLORS)], count=20, speed=120)
                    idx = self.level - 1
                    mr, mc = MONSTER_STARTS[idx][m.idx]
                    m.respawn(mr, mc)
                else:
                    self._player_caught()
                    return

        # ── Level complete check ──────────────────────────────────────────────
        if self.grid.is_complete():
            self._level_complete()

        # ── Flash decay ───────────────────────────────────────────────────────
        if self._flash > 0:
            self._flash = max(0.0, self._flash - dt * 3)

        # ── Particles ─────────────────────────────────────────────────────────
        for p in self.particles:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['life'] -= dt
        self.particles = [p for p in self.particles if p['life'] > 0]
        
        # Emit dust if player moving
        if self.player.moving and random.random() < 0.2:
            px, py = self.player.get_render_pos()
            self.spawn_particles(px, py + CELL_SIZE//2, (150, 130, 100), count=1, speed=20)

    # ── State transitions ─────────────────────────────────────────────────────
    def _player_caught(self):
        self.lives -= 1
        self._flash = 1.0
        px, py = self.player.get_render_pos()
        self.spawn_particles(px, py, (255, 0, 0), count=30, speed=150)
        if self.lives <= 0:
            self.state = ST_GAMEOVER
            self.play_sound('game_over')
        else:
            self.play_sound('caught')
            # Respawn everything
            idx = self.level - 1
            pr, pc = PLAYER_STARTS[idx]
            self.player.respawn(pr, pc)
            for i, m in enumerate(self.monsters):
                mr, mc = MONSTER_STARTS[idx][i]
                m.respawn(mr, mc)

    def _level_complete(self):
        bonus = SCORE_LEVEL_WIN + self.lives * SCORE_LIFE_BONUS
        self.score += bonus
        if self.level >= MAX_LEVELS:
            self.state = ST_WIN
            self.play_sound('win')
        else:
            self.state = ST_LVLDONE
            self.play_sound('win')

    # ── Render ────────────────────────────────────────────────────────────────
    def _render(self):
        time_ms = pygame.time.get_ticks()
        surf = self.screen
        surf.fill(C_BG)

        if self.state == ST_MENU:
            self._render_menu(time_ms)
        else:
            self._render_game(time_ms)
            self._render_overlays(time_ms)

        pygame.display.flip()

    def _render_game(self, time_ms):
        # ── Grid & Items ──────────────────────────────────────────────────────
        if self.grid:
            for r in range(GRID_ROWS):
                for c in range(GRID_COLS):
                    ct = self.grid.get(r, c)
                    is_tr = (r, c) in self.grid.traversed
                    _draw_cell(self.screen, r, c, ct, is_tr, time_ms)
            
            for (r, c), data in self.active_items.items():
                _draw_item(self.screen, r, c, data['type'], time_ms)

        # ── Entities ──────────────────────────────────────────────────────────
        if self.monsters:
            for m in self.monsters:
                _draw_monster(self.screen, m, time_ms)

        if self.player:
            _draw_player(self.screen, self.player, time_ms)

        # ── Particles ─────────────────────────────────────────────────────────
        for p in self.particles:
            alpha = max(0, int((p['life'] / p['max_life']) * 255))
            c = (*p['col'], alpha)
            s = pygame.Surface((p['size']*2, p['size']*2), pygame.SRCALPHA)
            pygame.draw.circle(s, c, (p['size'], p['size']), p['size'])
            self.screen.blit(s, (int(p['x'] - p['size']), int(p['y'] - p['size'])))

        # ── Death flash overlay ───────────────────────────────────────────────
        if self._flash > 0:
            s = pygame.Surface((GAME_AREA_W, SCREEN_H - HEADER_H), pygame.SRCALPHA)
            s.fill((255, 30, 30, int(self._flash * 140)))
            self.screen.blit(s, (0, HEADER_H))

        # ── Header & sidebar ──────────────────────────────────────────────────
        _draw_header(self.screen, self, time_ms)
        _draw_sidebar(self.screen, self, time_ms)

    def _render_overlays(self, time_ms):
        if self.state == ST_PAUSED:
            _overlay(self.screen, 'PAUSED', 'Take a breath…', C_TEXT_GOLD,
                     'Press P or ESC to resume')
        elif self.state == ST_LVLDONE:
            bonus = SCORE_LEVEL_WIN + self.lives * SCORE_LIFE_BONUS
            _overlay(self.screen,
                     f'LEVEL {self.level} CLEARED!',
                     f'+{bonus:,} points  ·  Prepare for Level {self.level + 1}',
                     C_TEXT_GREEN)
        elif self.state == ST_GAMEOVER:
            _overlay(self.screen, 'CAPTURED!',
                     f'Final Score: {self.score:,}',
                     C_TEXT_RED, 'Press ENTER to return to menu')
        elif self.state == ST_WIN:
            _overlay(self.screen, '🏆  ESCAPED!',
                     f'You beat all {MAX_LEVELS} levels!  Score: {self.score:,}',
                     C_TEXT_GOLD, 'Press ENTER to play again')

    def _render_menu(self, time_ms):
        self.screen.fill(C_BG)
        cx, cy = SCREEN_W // 2, SCREEN_H // 2

        # Animated dots grid in background
        for r in range(0, SCREEN_H, 40):
            for c in range(0, SCREEN_W, 40):
                phase = math.sin((time_ms / 800) + r * 0.05 + c * 0.05)
                alpha = int(30 + 25 * phase)
                pygame.draw.circle(self.screen, (40, 50, 120), (c, r), 2)

        # Title
        pulse = 0.5 + 0.5 * math.sin(time_ms / 500)
        tc = tuple(int(a + (b - a) * pulse) for a, b in zip(C_TEXT_GOLD, C_PLAYER_SPEED))
        _text(self.screen, 'ESCAPE X', 70, tc, (cx, cy - 110), bold=True, anchor='center')
        _text(self.screen, 'Cover every cell of the grid to escape!',
              18, C_TEXT_SECONDARY, (cx, cy - 50), anchor='center')

        # Info box
        box = pygame.Rect(cx - 200, cy - 20, 400, 180)
        pygame.draw.rect(self.screen, (12, 12, 40), box, border_radius=12)
        pygame.draw.rect(self.screen, C_SIDEBAR_LINE, box, 2, border_radius=12)

        info = [
            ('🟡', 'X',       'You — cover ALL cells to win'),
            ('🔴', 'Monsters','Chase you with evolving AI'),
            ('⬛', 'Tar',     f'Slows you for {TAR_DUR:.0f}s'),
            ('👁', 'Stealth', f'Hidden from ghosts for {STEALTH_DUR:.0f}s'),
            ('💨', 'Speed',   f'Speed boost for {SPEED_DUR:.0f}s'),
            ('❄',  'Frost',   f'Freezes you for {FROST_DUR:.0f}s'),
            ('🔥', 'Fire',    f'Kills ghosts for {FIRE_DUR:.0f}s!'),
        ]
        for i, (icon, name, desc) in enumerate(info):
            iy = cy - 10 + i * 26
            _text(self.screen, f'{icon} {name:9s} — {desc}', 14,
                  C_TEXT_PRIMARY, (cx - 185, iy))

        # Start prompt
        blink = int(time_ms / 500) % 2 == 0
        if blink:
            _text(self.screen, '▶  Press ENTER or SPACE to Start',
                  18, C_TEXT_GOLD, (cx, cy + 175), bold=True, anchor='center')

        # Level preview
        _text(self.screen, f'{MAX_LEVELS} Levels  ·  4 Monsters  ·  6 AI Algorithms',
              13, C_TEXT_SECONDARY, (cx, cy + 205), anchor='center')
