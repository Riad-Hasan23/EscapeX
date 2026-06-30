# =============================================================================
#  level_data.py — Five pre-designed 20×20 mazes for EscapeX
# =============================================================================
from constants import (EMPTY, WALL,
                       GRID_ROWS, GRID_COLS)


import random

def is_ghost_house(r, c):
    """Returns True if (r, c) is within the central ghost house area (including moat)."""
    return 7 <= r <= 11 and 6 <= c <= 14

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

    # 2. Build the Ghost House Moat
    for r in range(7, 12):
        for c in range(6, 15):
            g[r][c] = EMPTY
            
    # Ghost House Walls (1-thick)
    for r in range(8, 11):
        for c in range(7, 14):
            g[r][c] = WALL
    
    # Interior (5x1)
    for c in range(8, 13):
        g[9][c] = EMPTY
    
    # Ghost house exit
    g[10][10] = EMPTY

    # 3. Add loops (knock down random walls)
    # Lower levels have some loops. Higher levels have almost none (harder).
    loops = max(2, 20 - level_idx * 5)
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

# Monster spawn positions (row, col) — 2 on left, 2 on right
MONSTER_STARTS = [
    [(9, 8), (9, 9), (9, 11), (9, 12)],
    [(9, 8), (9, 9), (9, 11), (9, 12)],
    [(9, 8), (9, 9), (9, 11), (9, 12)],
    [(9, 8), (9, 9), (9, 11), (9, 12)],
    [(9, 8), (9, 9), (9, 11), (9, 12)],
]
