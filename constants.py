# =============================================================================
#  constants.py — All game-wide constants for EscapeX
# =============================================================================

# ── Display ──────────────────────────────────────────────────────────────────
CELL_SIZE      = 30          # pixels per grid cell
GRID_COLS      = 21
GRID_ROWS      = 21
GAME_AREA_W    = CELL_SIZE * GRID_COLS   # 630
SIDEBAR_W      = 230
SCREEN_W       = GAME_AREA_W + SIDEBAR_W  # 830
HEADER_H       = 58
SCREEN_H       = CELL_SIZE * GRID_ROWS + HEADER_H  # 658
FPS            = 60

# ── Cell types ───────────────────────────────────────────────────────────────
EMPTY       = 0
WALL        = 1
TAR         = 2   # slows entity
SPEED       = 3   # speeds entity
STEALTH     = 4   # makes player invisible to ghosts
FROST       = 5   # freezes entity
FIRE        = 7   # allows player to kill ghosts
TRAVERSED   = 6   # visual marker only (stored separately)

# ── Colour palette (Classy Pirate Theme) ───────────────────────────────────────
C_BG              = (15,  10,   5)
C_HEADER_BG       = (10,   5,   2)
C_SIDEBAR_BG      = (10,   5,   2)
C_SIDEBAR_LINE    = (120, 80,  40)

C_WALL            = (60,  40,  20)
C_WALL_EDGE       = (90,  60,  30)
C_WALL_INNER      = (40,  25,  10)

C_EMPTY           = (20,  15,  10)
C_TRAVERSED       = (35,  25,  15)
C_DOT             = (255, 215,  0)  # Gold coin

C_TAR             = (90,  55,  18)
C_TAR_BORDER      = (140, 90,  30)
C_SPEED         = (70, 165, 240)
C_SPEED_BORDER  = (130, 210, 255)
C_STEALTH       = (120, 120, 150)
C_STEALTH_BORDER= (200, 200, 230)
C_FROST          = (145, 205, 252)
C_FROST_BORDER   = (200, 235, 255)
C_FIRE           = (240,  80,  40)
C_FIRE_BORDER    = (255, 180,  50)

C_PLAYER          = (255, 220,   0)
C_PLAYER_OUTLINE  = (255, 155,   0)
C_PLAYER_TAR      = (160, 100,  30)
C_PLAYER_SPEED  = ( 70, 190, 255)
C_PLAYER_STEALTH= ( 60,  60,  90)  # darker/transparent look
C_PLAYER_FROST   = (190, 230, 255)
C_PLAYER_FROZEN   = (160, 210, 255)  # while freeze effect is active
C_PLAYER_FIRE     = (255, 100,  20)

MONSTER_COLORS = [
    (255,  55,  55),   # Rex   — Red
    (255, 148,  38),   # Blaze — Orange
    ( 38, 218, 138),   # Surge — Cyan-Green
    (210,  50, 220),   # Hex   — Purple
]
MONSTER_NAMES = ['Rex', 'Blaze', 'Surge', 'Hex']

C_TEXT_PRIMARY   = (220, 225, 255)
C_TEXT_SECONDARY = (140, 150, 200)
C_TEXT_GOLD      = (255, 215,  60)
C_TEXT_GREEN     = ( 60, 230, 120)
C_TEXT_RED       = (255,  70,  70)

# ── Speed settings (pixels / second) ─────────────────────────────────────────
PLAYER_SPEED    = 90    # baseline (~3 cells/sec at CELL_SIZE=30)
TAR_MULT        = 0.35
SPEED_MULT    = 2.2

# Effect durations (seconds)
TAR_DUR         = 4.0
SPEED_DUR     = 3.0
STEALTH_DUR   = 5.0
FROST_DUR      = 2.5
FIRE_DUR       = 6.0

# Dynamic Item spawning
ITEM_SPAWN_INTERVAL = 10.0
ITEM_DESPAWN_TIME   = 8.0
MAX_ITEMS           = 2

# Monster speeds per level (index 0 = level 1)
MONSTER_SPEEDS  = [80, 95, 115, 135, 160]
# How often a monster recomputes its path (seconds)
MONSTER_RECOMPUTE = 0.25

# ── Directions: (dcol, drow) tuples ──────────────────────────────────────────
DIR_UP    = ( 0, -1)
DIR_DOWN  = ( 0,  1)
DIR_LEFT  = (-1,  0)
DIR_RIGHT = ( 1,  0)
ALL_DIRS  = [DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT]

# ── Algorithm IDs ─────────────────────────────────────────────────────────────
ALGO_RANDOM    = 'random'
ALGO_DFS       = 'dfs'
ALGO_BFS       = 'bfs'
ALGO_BACKTRACK = 'backtrack'
ALGO_DIJKSTRA  = 'dijkstra'
ALGO_ASTAR     = 'astar'

ALGO_DISPLAY = {
    ALGO_RANDOM:    'Random Walk',
    ALGO_DFS:       'Depth-First',
    ALGO_BFS:       'Breadth-First',
    ALGO_BACKTRACK: 'Backtracking',
    ALGO_DIJKSTRA:  'Dijkstra',
    ALGO_ASTAR:     'A*  Optimal',
}

# Monster algorithm config per level (4 monsters)
LEVEL_CONFIGS = [
    [ALGO_BFS,      ALGO_DFS,      ALGO_ASTAR,    ALGO_RANDOM],
    [ALGO_BFS,      ALGO_DIJKSTRA, ALGO_ASTAR,    ALGO_ASTAR],
    [ALGO_DIJKSTRA, ALGO_ASTAR,    ALGO_ASTAR,    ALGO_ASTAR],
    [ALGO_ASTAR,    ALGO_ASTAR,    ALGO_ASTAR,    ALGO_ASTAR],
    [ALGO_ASTAR,    ALGO_ASTAR,    ALGO_ASTAR,    ALGO_ASTAR],
]

MAX_LEVELS = 5

# ── Game states ───────────────────────────────────────────────────────────────
ST_MENU     = 'menu'
ST_PLAYING  = 'playing'
ST_PAUSED   = 'paused'
ST_LVLDONE  = 'lvl_done'
ST_GAMEOVER = 'game_over'
ST_WIN      = 'win'

# ── Scoring ───────────────────────────────────────────────────────────────────
SCORE_STEP      = 10
SCORE_LEVEL_WIN = 1000
SCORE_LIFE_BONUS = 300
SCORE_KILL_GHOST = 200
LIVES           = 3

# ── Alignment tolerance for direction buffering ───────────────────────────────
ALIGN_TOLERANCE = 4   # pixels; within this distance of cell centre → can turn
