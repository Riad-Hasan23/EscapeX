# =============================================================================
#  algorithms.py — Pathfinding algorithms used by the monsters
# =============================================================================
import random
import heapq
from collections import deque
from constants import (WALL, TAR, SPEED, STEALTH, FROST, FIRE,
                       GRID_ROWS, GRID_COLS,
                       ALGO_RANDOM, ALGO_DFS, ALGO_BFS,
                       ALGO_BACKTRACK, ALGO_DIJKSTRA, ALGO_ASTAR)


# ── Neighbour enumeration ─────────────────────────────────────────────────────
def get_passable_neighbours(pos, grid):
    """Return all grid (row, col) tuples adjacent to pos that are not walls."""
    r, c = pos
    neighbours = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS and grid[nr][nc] != WALL:
            neighbours.append((nr, nc))
    return neighbours


# ── Obstacle cost map for weighted algorithms ─────────────────────────────────
_COST = {WALL: 999, TAR: 4, FROST: 5, SPEED: 1, FIRE: 1}

def cell_cost(grid, r, c):
    return _COST.get(grid[r][c], 1)


# ── Path reconstruction helper ────────────────────────────────────────────────
def _reconstruct(came_from, start, end):
    path = []
    cur = end
    while cur != start:
        path.append(cur)
        cur = came_from[cur]
    path.reverse()
    return path


# ── Random Walk ───────────────────────────────────────────────────────────────
def _random_walk(start, _target, grid):
    """Returns one random step (monster wanders)."""
    nbrs = get_passable_neighbours(start, grid)
    if not nbrs:
        return []
    return [random.choice(nbrs)]


# ── Breadth-First Search ──────────────────────────────────────────────────────
def _bfs(start, target, grid):
    if start == target:
        return []
    came_from = {start: None}
    queue = deque([start])
    while queue:
        pos = queue.popleft()
        if pos == target:
            return _reconstruct(came_from, start, target)
        for nb in get_passable_neighbours(pos, grid):
            if nb not in came_from:
                came_from[nb] = pos
                queue.append(nb)
    return []


# ── Depth-First Search ────────────────────────────────────────────────────────
def _dfs(start, target, grid):
    """DFS — explores deeply; can be erratic (good for mid-levels)."""
    if start == target:
        return []
    came_from = {start: None}
    stack = [start]
    while stack:
        pos = stack.pop()
        if pos == target:
            return _reconstruct(came_from, start, target)
        nbrs = get_passable_neighbours(pos, grid)
        random.shuffle(nbrs)          # shuffled so it isn't always same path
        for nb in nbrs:
            if nb not in came_from:
                came_from[nb] = pos
                stack.append(nb)
    return []


# ── Backtracking DFS ──────────────────────────────────────────────────────────
def _backtrack(start, target, grid):
    """Recursive backtracking — fully explores, then returns first found path."""
    if start == target:
        return []
    visited = {start}
    path = []

    def dfs(pos):
        if pos == target:
            return True
        nbrs = get_passable_neighbours(pos, grid)
        random.shuffle(nbrs)
        for nb in nbrs:
            if nb not in visited:
                visited.add(nb)
                path.append(nb)
                if dfs(nb):
                    return True
                path.pop()
        return False

    dfs(start)
    return path


# ── Dijkstra ──────────────────────────────────────────────────────────────────
def _dijkstra(start, target, grid):
    """Shortest weighted path — avoids costly cells."""
    if start == target:
        return []
    dist = {start: 0}
    came_from = {start: None}
    heap = [(0, start)]
    while heap:
        d, pos = heapq.heappop(heap)
        if pos == target:
            return _reconstruct(came_from, start, target)
        if d > dist.get(pos, float('inf')):
            continue
        for nb in get_passable_neighbours(pos, grid):
            nr, nc = nb
            nd = d + cell_cost(grid, nr, nc)
            if nd < dist.get(nb, float('inf')):
                dist[nb] = nd
                came_from[nb] = pos
                heapq.heappush(heap, (nd, nb))
    return []


# ── A* ────────────────────────────────────────────────────────────────────────
def _astar(start, target, grid):
    """A* with Manhattan heuristic — optimal and fastest pursuit."""
    if start == target:
        return []

    def h(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    g_score = {start: 0}
    came_from = {start: None}
    heap = [(h(start, target), 0, start)]
    while heap:
        _f, g, pos = heapq.heappop(heap)
        if pos == target:
            return _reconstruct(came_from, start, target)
        if g > g_score.get(pos, float('inf')):
            continue
        for nb in get_passable_neighbours(pos, grid):
            nr, nc = nb
            ng = g + cell_cost(grid, nr, nc)
            if ng < g_score.get(nb, float('inf')):
                g_score[nb] = ng
                came_from[nb] = pos
                heapq.heappush(heap, (ng + h(nb, target), ng, nb))
    return []


# ── Public dispatch ───────────────────────────────────────────────────────────
_ALGO_FN = {
    ALGO_RANDOM:    _random_walk,
    ALGO_DFS:       _dfs,
    ALGO_BFS:       _bfs,
    ALGO_BACKTRACK: _backtrack,
    ALGO_DIJKSTRA:  _dijkstra,
    ALGO_ASTAR:     _astar,
}

def find_path(algo, start, target, grid):
    """
    Compute a path from *start* to *target* using *algo*.

    Returns a list of (row, col) tuples (not including start).
    Returns an empty list if no path exists or only one step for random.
    """
    fn = _ALGO_FN.get(algo, _random_walk)
    try:
        return fn(start, target, grid)
    except Exception:
        return []
