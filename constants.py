# =============================================================================
#  constants.py — All game-wide constants for EscapeX
# =============================================================================

# ── Display ──────────────────────────────────────────────────────────────────
CELL_SIZE      = 30          # pixels per grid cell
GRID_COLS      = 20
GRID_ROWS      = 20
GAME_AREA_W    = CELL_SIZE * GRID_COLS   # 600
SIDEBAR_W      = 230
SCREEN_W       = GAME_AREA_W + SIDEBAR_W  # 830
HEADER_H       = 58
SCREEN_H       = CELL_SIZE * GRID_ROWS + HEADER_H  # 658
FPS            = 60

# ── Cell types ───────────────────────────────────────────────────────────────
EMPTY       = 0
WALL        = 1
MUD         = 2   # slows entity
SLIPPER     = 3   # speeds entity
INVISIBLE   = 4   # makes player invisible to ghosts
FREEZE_CELL = 5   # freezes entity
TRAVERSED   = 6   # visual marker only (stored separately)

# ── Colour palette (dark‑neon theme) ─────────────────────────────────────────
C_BG              = (8,  8,  28)
C_HEADER_BG       = (4,  4,  18)
C_SIDEBAR_BG      = (4,  4,  18)
C_SIDEBAR_LINE    = (25, 40, 110)

C_WALL            = (28,  68, 195)
C_WALL_EDGE       = (55, 115, 240)
C_WALL_INNER      = (18,  45, 130)

C_EMPTY           = (10,  10,  34)
C_TRAVERSED       = (12,  42,  72)
C_DOT             = (50,  55, 100)

C_MUD             = (90,  55,  18)
C_MUD_BORDER      = (140, 90,  30)
C_SLIPPER         = (70, 165, 240)
C_SLIPPER_BORDER  = (130, 210, 255)
C_INVISIBLE       = (120, 120, 150)
C_INVISIBLE_BORDER= (200, 200, 230)
C_FREEZE          = (145, 205, 252)
C_FREEZE_BORDER   = (200, 235, 255)

C_PLAYER          = (255, 220,   0)
C_PLAYER_OUTLINE  = (255, 155,   0)
C_PLAYER_MUD      = (160, 100,  30)
C_PLAYER_SLIPPER  = ( 70, 190, 255)
C_PLAYER_INVISIBLE= ( 60,  60,  90)  # darker/transparent look
C_PLAYER_FREEZE   = (190, 230, 255)
C_PLAYER_FROZEN   = (160, 210, 255)  # while freeze effect is active

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
MUD_MULT        = 0.35
SLIPPER_MULT    = 2.2

# Effect durations (seconds)
MUD_DUR         = 4.0
SLIPPER_DUR     = 3.0
INVISIBLE_DUR   = 5.0
FREEZE_DUR      = 2.5   # user-requested freeze attribute

# Dynamic Item spawning
ITEM_SPAWN_INTERVAL = 6.0
ITEM_DESPAWN_TIME   = 12.0
MAX_ITEMS           = 2

# Monster speeds per level (index 0 = level 1)
MONSTER_SPEEDS  = [65, 74, 84, 95, 110]
# How often a monster recomputes its path (seconds)
MONSTER_RECOMPUTE = 0.45

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
    [ALGO_RANDOM,   ALGO_RANDOM,   ALGO_RANDOM,   ALGO_RANDOM],
    [ALGO_RANDOM,   ALGO_DFS,      ALGO_BFS,      ALGO_RANDOM],
    [ALGO_DFS,      ALGO_BFS,      ALGO_BACKTRACK, ALGO_DIJKSTRA],
    [ALGO_BFS,      ALGO_DIJKSTRA, ALGO_ASTAR,    ALGO_ASTAR],
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
LIVES           = 3

# ── Alignment tolerance for direction buffering ───────────────────────────────
ALIGN_TOLERANCE = 4   # pixels; within this distance of cell centre → can turn
