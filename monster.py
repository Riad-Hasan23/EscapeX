# =============================================================================
#  monster.py — AI-driven ghost/monster entities
# =============================================================================
import random
from entity import Entity
from algorithms import find_path
from constants import CELL_SIZE, MONSTER_RECOMPUTE, ALGO_RANDOM


class Monster(Entity):
    """
    A monster that chases the player using an assigned pathfinding algorithm.
    """

    def __init__(self, idx: int, start_row: int, start_col: int,
                 speed: float, algorithm: str):
        super().__init__(start_row, start_col, speed)
        self.idx = idx                  # 0-3 for colour / name lookup
        self.algorithm = algorithm
        self._path: list = []           # remaining waypoints
        self._recompute_timer = 0.0

    # ── Algorithm swap (called on level change) ───────────────────────────────
    def set_algorithm(self, algo: str):
        self.algorithm = algo
        self._path.clear()

    # ── Main update ───────────────────────────────────────────────────────────
    def update(self, dt: float, grid, player_pos: tuple, player_invisible: bool):
        """Advance monster by dt seconds."""
        if self.tick_effects(dt):
            return  # frozen

        self._recompute_timer -= dt

        if self.moving:
            arrived = self._advance(dt)
            if arrived:
                self._step(grid, player_pos, player_invisible)
        else:
            self._step(grid, player_pos, player_invisible)

    # ── Step logic ────────────────────────────────────────────────────────────
    def _step(self, grid, player_pos: tuple, player_invisible: bool):
        # Force random walk if player is invisible
        algo_to_use = ALGO_RANDOM if player_invisible else self.algorithm

        # If player became invisible/visible, or timer expired, or path empty -> recompute
        if self._recompute_timer <= 0 or not self._path or player_invisible:
            self._path = find_path(
                algo_to_use,
                (self.row, self.col),
                player_pos,
                grid.data,
            )
            self._recompute_timer = MONSTER_RECOMPUTE

        if self._path:
            next_pos = self._path.pop(0)
            nr, nc = next_pos
            if grid.is_passable(nr, nc):
                self._start_move(nr, nc)
            else:
                self._path.clear()
                self._random_step(grid)
        else:
            self._random_step(grid)

    def _random_step(self, grid):
        from algorithms import get_passable_neighbours
        nbrs = get_passable_neighbours((self.row, self.col), grid.data)
        if nbrs:
            nr, nc = random.choice(nbrs)
            self._start_move(nr, nc)

    # ── Respawn ───────────────────────────────────────────────────────────────
    def respawn(self, start_row: int, start_col: int):
        self.t_row = start_row
        self.t_col = start_col
        self.row = start_row
        self.col = start_col
        self.t = 0.0
        self.moving = False
        self.clear_effects()
        self._path.clear()
        self._recompute_timer = 0.0
        self.px, self.py = self._centre(start_row, start_col)
