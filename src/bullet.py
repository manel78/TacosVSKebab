# projectile du joueur.
# Avance dans une direction et disparaît hors écran.
from __future__ import annotations
import pygame
from .settings import WIDTH, HEIGHT


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, direction: pygame.Vector2) -> None:
        super().__init__()

        #placeholder c'est pas une vrai valeur

        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 90, 70), (5, 5), 5)

        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(self.rect.centerx, self.rect.centery)

        # normalisée
        self.dir = pygame.Vector2(direction)
        if self.dir.length_squared() > 0:
            self.dir = self.dir.normalize()

        self.speed = 620
        self.damage = 1

    def update(self, dt: float) -> None:
        self.pos += self.dir * self.speed * dt
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        # supprime la bullet quand elle sort de l'écran
        if (
            self.rect.right < 0 or self.rect.left > WIDTH
            or self.rect.bottom < 0 or self.rect.top > HEIGHT
        ):
            self.kill()
