# Tout ce qui est affichage textes.
# Ça évite de mettre du render de texte partout dans les scènesadapter avec du html

from __future__ import annotations
import pygame
from .settings import WHITE, GRAY, YELLOW, RED
from .utils import draw_text


class UI:
    def __init__(self) -> None:
        # Police simple (si pas dispo, pygame prend une police par défaut)
        self.font = pygame.font.SysFont("consolas", 20)
        self.big = pygame.font.SysFont("consolas", 36)

    def draw_hud(self, screen: pygame.Surface, hp: int, score: int, room_index: int, items: list[str]) -> None:
        # On garde un HUD basique pour l’instant.
        draw_text(screen, f"HP: {hp}", (12, 10), self.font, RED if hp <= 1 else WHITE)
        draw_text(screen, f"Score: {score}", (12, 34), self.font, WHITE)
        draw_text(screen, f"Salle: {room_index}/4", (12, 58), self.font, GRAY)
        draw_text(screen, f"Items: {', '.join(items) if items else '-'}", (12, 82), self.font, YELLOW)

    def draw_center_title(self, screen: pygame.Surface, title: str, subtitle: str | None = None) -> None:
        w, h = screen.get_size()

        title_img = self.big.render(title, True, WHITE)
        screen.blit(title_img, (w // 2 - title_img.get_width() // 2, h // 2 - 80))

        if subtitle:
            sub_img = self.font.render(subtitle, True, GRAY)
            screen.blit(sub_img, (w // 2 - sub_img.get_width() // 2, h // 2 - 30))
