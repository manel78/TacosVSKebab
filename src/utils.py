# évite mêmes fonctions.
from __future__ import annotations
import pygame


def clamp(value: float, lo: float, hi: float) -> float:
    """Bloque une valeur entre lo et hi."""
    return max(lo, min(hi, value))


def draw_text(
    surface: pygame.Surface,
    text: str,
    pos: tuple[int, int],
    font: pygame.font.Font,
    color: tuple[int, int, int],
) -> None:
    """Affiche un texte simple à l’écran."""
    img = font.render(text, True, color)
    surface.blit(img, pos)
