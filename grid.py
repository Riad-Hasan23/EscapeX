# =============================================================================
#  grid.py — Grid data-model for EscapeX
# =============================================================================
from constants import (WALL, EMPTY, MUD, SLIPPER, INVISIBLE, FREEZE_CELL,
                       GRID_ROWS, GRID_COLS)


class Grid:
    """
    Wraps the 2-D cell array for a single level.

    The original layout is kept so the level can be fully reset.
    A separate traversal-set records which walkable cells X has visited.
    """

    def __init__(self, data):
        # Deep copy so mutations don't affect the master copy in level_data.py
        self.data = [row[:] for row in data]
        self._original = [row[:] for row in data]

        # Pre-compute walkable count (everything that's not a wall)
        self._walkable = sum(
            1 for r in range(GRID_ROWS)
            for c in range(GRID_COLS)
            if data[r][c] != WALL
        )
        self.traversed: set = set()

    # ── Cell access ──────────────────────────────────────────────────────────
    def get(self, row, col):
        return self.data[row][col]

    def is_wall(self, row, col):
        if row < 0 or row >= GRID_ROWS or col < 0 or col >= GRID_COLS:
            return True
        return self.data[row][col] == WALL

    def is_passable(self, row, col):
        return not self.is_wall(row, col)

    # ── Traversal ─────────────────────────────────────────────────────────────
    def mark_traversed(self, row, col):
        """Mark a walkable cell as visited by the player. Returns True if new."""
        if self.is_wall(row, col):
            return False
        if (row, col) not in self.traversed:
            self.traversed.add((row, col))
            return True
        return False

    def traversal_pct(self) -> float:
        if self._walkable == 0:
            return 100.0
        return min(100.0, (len(self.traversed) / self._walkable) * 100.0)

    def is_complete(self) -> bool:
        return len(self.traversed) >= self._walkable

    # ── Reset ─────────────────────────────────────────────────────────────────
    def reset(self):
        self.data = [row[:] for row in self._original]
        self.traversed.clear()

    # ── Utility ───────────────────────────────────────────────────────────────
    def cell_type_at(self, row, col):
        """Return raw cell type integer at (row, col), or WALL if out-of-bounds."""
        if row < 0 or row >= GRID_ROWS or col < 0 or col >= GRID_COLS:
            return WALL
        return self.data[row][col]
