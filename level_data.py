# =============================================================================
#  level_data.py — Five pre-designed 20×20 mazes for EscapeX
# =============================================================================
from constants import (EMPTY, WALL, MUD, SLIPPER, INVISIBLE, FREEZE_CELL,
                       GRID_ROWS, GRID_COLS)


import random

def is_ghost_house(r, c):
    """Returns True if (r, c) is within the central 5x5 ghost house area."""
    return 8 <= r <= 12 and 8 <= c <= 12

def generate_level_grid(level_idx: int):
    """
    Procedurally generates a perfect maze using Recursive Backtracking,
    adds a central ghost house, and creates random loops to prevent dead-ends.
    """
    g = [[WALL] * GRID_COLS for _ in range(GRID_ROWS)]

    def get_unvisited_neighbors(r, c):
        nbrs = []
        for dr, dc in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            nr, nc = r + dr, c + dc
            if 1 <= nr < GRID_ROWS - 1 and 1 <= nc < GRID_COLS - 1:
                # Don't carve into ghost house area
                if g[nr][nc] == WALL and not is_ghost_house(nr, nc) and not is_ghost_house(r + dr//2, c + dc//2):
                    nbrs.append((nr, nc, r + dr//2, c + dc//2))
        return nbrs

    # 1. Carve a perfect maze using DFS
    stack = [(1, 1)]
    g[1][1] = EMPTY
    
    while stack:
        r, c = stack[-1]
        nbrs = get_unvisited_neighbors(r, c)
        if nbrs:
            nr, nc, wr, wc = random.choice(nbrs)
            g[wr][wc] = EMPTY
            g[nr][nc] = EMPTY
            stack.append((nr, nc))
        else:
            stack.pop()

    # 2. Build the Ghost House (Center 5x5)
    for r in range(8, 13):
        for c in range(8, 13):
            g[r][c] = EMPTY
    
    for c in range(8, 13):
        g[8][c] = WALL
        g[12][c] = WALL
    for r in range(8, 13):
        g[r][8] = WALL
        g[r][12] = WALL
    
    # Ghost house exit
    g[12][10] = EMPTY
    g[13][10] = EMPTY  # Ensure the exit connects to the grid

    # 3. Add loops (knock down random walls)
    # Lower levels have more loops (easier). Higher levels have fewer loops (harder).
    loops = max(5, 30 - level_idx * 5)
    attempts = 200
    while loops > 0 and attempts > 0:
        attempts -= 1
        r = random.randint(1, GRID_ROWS - 2)
        c = random.randint(1, GRID_COLS - 2)
        if g[r][c] == WALL and not is_ghost_house(r, c):
            # If the wall separates two vertical empty spaces
            if g[r-1][c] == EMPTY and g[r+1][c] == EMPTY and g[r][c-1] == WALL and g[r][c+1] == WALL:
                g[r][c] = EMPTY
                loops -= 1
            # If the wall separates two horizontal empty spaces
            elif g[r][c-1] == EMPTY and g[r][c+1] == EMPTY and g[r-1][c] == WALL and g[r+1][c] == WALL:
                g[r][c] = EMPTY
                loops -= 1

    return g


# Player start (row, col) — always top-left open cell
PLAYER_STARTS = [
    (1, 1),
    (1, 1),
    (1, 1),
    (1, 1),
    (1, 1),
]

# Monster spawn positions (row, col) — inside ghost house interior (rows 9-11, cols 9-11)
MONSTER_STARTS = [
    [(9, 9), (9, 11), (11, 9), (11, 11)],
    [(9, 9), (9, 11), (11, 9), (11, 11)],
    [(9, 9), (9, 11), (11, 9), (11, 11)],
    [(9, 9), (9, 11), (11, 9), (11, 11)],
    [(9, 9), (9, 11), (11, 9), (11, 11)],
]
