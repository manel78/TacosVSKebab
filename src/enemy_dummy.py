# ennemi test
# Le nombre de coups = hp (vu que joueur fait 1 dégât par attaque).

from __future__ import annotations
import pygame


class EnemyDummy(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, hp: int = 4, size: int = 46) -> None:
        super().__init__()

        self.max_hp = hp
        self.hp = hp

        # Couleur selon avec le type genre gros ennemi
        if hp >= 8:
            color = (70, 170, 70)     # gros
        elif hp >= 6:
            color = (90, 200, 90)     # moyen
        else:
            color = (120, 220, 120)   # petit

        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(self.image, color, self.image.get_rect(), border_radius=10)
        pygame.draw.rect(self.image, (30, 30, 30), self.image.get_rect(), 2, border_radius=10)

        self.rect = self.image.get_rect(center=(x, y))

    def take_damage(self, amount: int) -> None:
        self.hp -= amount
        if self.hp <= 0:
            self.kill()
