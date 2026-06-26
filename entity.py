# =============================================================================
#  entity.py — Base class for Player and Monster
# =============================================================================
from constants import CELL_SIZE, HEADER_H


class Entity:
    """
    Grid-aligned entity with smooth pixel-level interpolation.

    Movement model (Pac-Man style):
      • Entity always knows its current cell (row, col).
      • When moving, it also knows its target cell (t_row, t_col).
      • A progress value  t ∈ [0, 1]  drives linear interpolation.
      • When t reaches 1 the entity "arrives" and picks the next target.
      • Pixel position (px, py) is always derived from row/col/t — the
        renderer only reads (px, py).

    Screen layout:
      col → x:  px = col * CELL_SIZE + CELL_SIZE // 2
      row → y:  py = HEADER_H + row * CELL_SIZE + CELL_SIZE // 2
    """

    HALF = CELL_SIZE // 2

    def __init__(self, start_row: int, start_col: int, speed: float):
        self.row = start_row
        self.col = start_col
        self.t_row = start_row
        self.t_col = start_col
        self.t = 0.0          # interpolation progress [0, 1]
        self.moving = False
        self.base_speed = speed
        self.speed = speed    # current pixels/second
        # direction vector (dc, dr) — col-first
        self.dir = (0, 0)
        # pixel position (screen coordinates)
        self.px, self.py = self._centre(start_row, start_col)

        # ── Shared effect state ───────────────────────────────────────────────
        self.effect = None       # 'mud' | 'slipper' | 'invisible' | 'freeze' | None
        self.effect_timer = 0.0
        self.frozen = False
        self.freeze_timer = 0.0
        self.invisible = False

    # ── Helpers ───────────────────────────────────────────────────────────────
    @staticmethod
    def _centre(row: int, col: int):
        px = col * CELL_SIZE + Entity.HALF
        py = HEADER_H + row * CELL_SIZE + Entity.HALF
        return px, py

    def _lerp_px(self):
        """Update pixel position from current interpolation state."""
        if not self.moving:
            self.px, self.py = self._centre(self.row, self.col)
        else:
            sx, sy = self._centre(self.row, self.col)
            ex, ey = self._centre(self.t_row, self.t_col)
            self.px = sx + (ex - sx) * self.t
            self.py = sy + (ey - sy) * self.t

    def get_grid_pos(self):
        """Return (row, col) of the cell the entity currently occupies."""
        return self.row, self.col

    def get_render_pos(self):
        """Return (px, py) screen-space coordinates for the renderer."""
        return int(self.px), int(self.py)

    # ── Effect management ─────────────────────────────────────────────────────
    def apply_effect(self, effect_type):
        """Called by the game manager when this entity consumes an item."""
        from constants import (MUD, SLIPPER, INVISIBLE, FREEZE_CELL,
                               MUD_MULT, SLIPPER_MULT,
                               MUD_DUR, SLIPPER_DUR, INVISIBLE_DUR, FREEZE_DUR)
        
        if effect_type == MUD:
            self.effect = 'mud'
            self.effect_timer = MUD_DUR
            self.speed = self.base_speed * MUD_MULT
        elif effect_type == SLIPPER:
            self.effect = 'slipper'
            self.effect_timer = SLIPPER_DUR
            self.speed = self.base_speed * SLIPPER_MULT
        elif effect_type == INVISIBLE:
            self.effect = 'invisible'
            self.effect_timer = INVISIBLE_DUR
            self.invisible = True
            self.speed = self.base_speed
        elif effect_type == FREEZE_CELL:
            self.effect = 'freeze'
            self.effect_timer = 0.0
            self.speed = self.base_speed
            self.frozen = True
            self.freeze_timer = FREEZE_DUR

    def tick_effects(self, dt: float):
        """Update active effect timers. Returns True if frozen (cannot move)."""
        if self.frozen:
            self.freeze_timer -= dt
            if self.freeze_timer <= 0:
                self.frozen = False
                self.freeze_timer = 0.0
            return True

        if self.effect and not self.frozen:
            self.effect_timer -= dt
            if self.effect_timer <= 0:
                self.effect = None
                self.effect_timer = 0.0
                self.invisible = False
                self.speed = self.base_speed
        return False

    def clear_effects(self):
        self.effect = None
        self.effect_timer = 0.0
        self.frozen = False
        self.freeze_timer = 0.0
        self.invisible = False
        self.speed = self.base_speed

    # ── Advance movement ──────────────────────────────────────────────────────
    def _advance(self, dt: float):
        """Move t forward by dt. Returns True if a cell boundary was crossed."""
        if not self.moving:
            return False
        step = self.speed * dt / CELL_SIZE
        self.t = min(1.0, self.t + step)
        self._lerp_px()
        if self.t >= 1.0:
            self.row = self.t_row
            self.col = self.t_col
            self.t = 0.0
            self.moving = False
            return True
        return False

    def _start_move(self, target_row: int, target_col: int):
        """Begin moving toward the given target cell."""
        self.t_row = target_row
        self.t_col = target_col
        self.dir = (target_col - self.col, target_row - self.row)
        self.t = 0.0
        self.moving = True
