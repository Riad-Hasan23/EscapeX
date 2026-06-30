# =============================================================================
#  main.py — Entry point for EscapeX
# =============================================================================
import sys
import pygame
from constants import SCREEN_W, SCREEN_H, FPS
from game import GameManager


def main():
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.init()
    pygame.display.set_caption('EscapeX')

    # Try to set a window icon (optional — no crash if it fails)
    try:
        icon = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(icon, (255, 220, 0), (16, 16), 14)
        f = pygame.font.SysFont('Segoe UI', 20, bold=True)
        lbl = f.render('X', True, (10, 10, 30))
        icon.blit(lbl, lbl.get_rect(center=(16, 16)))
        pygame.display.set_icon(icon)
    except Exception:
        pass

    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    gm = GameManager(screen)

    try:
        gm.run()
    except KeyboardInterrupt:
        pass
    finally:
        pygame.quit()


if __name__ == '__main__':
    main()
