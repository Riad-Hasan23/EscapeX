# =============================================================================
#  player.py — The X character
# =============================================================================
from entity import Entity
from constants import (
    PLAYER_SPEED,
    MUD, SLIPPER, INVISIBLE, FREEZE_CELL,
    MUD_MULT, MUD_DUR,
    SLIPPER_MULT, SLIPPER_DUR,
    INVISIBLE_DUR, FREEZE_DUR,
    DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT,
)


class Player(Entity):
    """
    Pac-Man style player:
      • Arrow keys set a *buffered* direction.
      • The buffer is applied the moment the player arrives at a new cell
        (i.e., when the current move completes) — if the new direction is
        passable.  Otherwise the previous direction is retried.
      • Speed modifiers (mud / slipper / invisible / freeze) are tracked with
        a remaining-timer approach.
    """

    def __init__(self, start_row: int, start_col: int):
        super().__init__(start_row, start_col, PLAYER_SPEED)
        self.next_dir = (0, 0)
        self.curr_dir = (0, 0)
        self.cells_visited = 0

    # ── Input ─────────────────────────────────────────────────────────────────
    def set_direction(self, dc: int, dr: int):
        self.next_dir = (dc, dr)

    # ── Main update ───────────────────────────────────────────────────────────
    def update(self, dt: float, grid):
        """Advance the player by dt seconds."""
        # Update inherited effects (freeze, speed modifiers)
        if self.tick_effects(dt):
            return False  # frozen

        if self.moving:
            arrived = self._advance(dt)
            if arrived:
                new_cell = grid.mark_traversed(self.row, self.col)
                if new_cell:
                    self.cells_visited += 1
                self._try_move(grid)
                return new_cell
            return False

        self._try_move(grid)
        return False

    # ── Movement attempt ──────────────────────────────────────────────────────
    def _try_move(self, grid):
        for dc, dr in [self.next_dir, self.curr_dir]:
            if dc == 0 and dr == 0:
                continue
            nr, nc = self.row + dr, self.col + dc
            if grid.is_passable(nr, nc):
                self.curr_dir = (dc, dr)
                self.next_dir = (0, 0)
                self._start_move(nr, nc)
                return

    # ── Teleport / respawn ─────────────────────────────────────────────────────
    def respawn(self, start_row: int, start_col: int):
        self.t_row = start_row
        self.t_col = start_col
        self.row = start_row
        self.col = start_col
        self.t = 0.0
        self.moving = False
        self.clear_effects()
        self.next_dir = (0, 0)
        self.curr_dir = (0, 0)
        self.px, self.py = self._centre(start_row, start_col)

    # ── Collision ─────────────────────────────────────────────────────────────
    def collides_with(self, monster) -> bool:
        from constants import CELL_SIZE
        dx = self.px - monster.px
        dy = self.py - monster.py
        threshold = CELL_SIZE * 0.60
        return (dx * dx + dy * dy) < threshold * threshold

    # ── Effect info for UI ────────────────────────────────────────────────────
    def get_effect_info(self):
        if self.frozen:
            return ('freeze', self.freeze_timer)
        return (self.effect, self.effect_timer)
