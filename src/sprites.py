# Player déplacement + tir IJKL
# EnemyDummy juste pour tester
# IMPORTANT:
# - ZQSD = bouger
# - IJKL = tirer
# - bullets -> collisions -> dégâts -> kill ennemi -> score
from __future__ import annotations
import pygame
from .settings import WIDTH, HEIGHT

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, direction: pygame.Vector2) -> None:
        super().__init__()
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 90, 70), (5, 5), 5)
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(self.rect.centerx, self.rect.centery)

        self.dir = pygame.Vector2(direction)
        if self.dir.length_squared() > 0:
            self.dir = self.dir.normalize()

        self.speed = 620
        self.damage = 1  # dégâts par bullet

    def update(self, dt: float) -> None:
        self.pos += self.dir * self.speed * dt
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        if (
            self.rect.right < 0 or self.rect.left > WIDTH
            or self.rect.bottom < 0 or self.rect.top > HEIGHT
        ):
            self.kill()

class EnemyDummy(pygame.sprite.Sprite):
    """
    Ennemi de test: ne bouge pas.
    Juste pour valider:
    - collisions bullet->enemy
    - HP enemy
    - disparition enemy
    """
    def __init__(self, x: int, y: int, hp: int = 3) -> None:
        super().__init__()
        self.image = pygame.Surface((46, 46), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (120, 220, 120), self.image.get_rect(), border_radius=10)
        self.rect = self.image.get_rect(center=(x, y))

        self.hp = hp

    def take_damage(self, amount: int) -> None:
        self.hp -= amount
        if self.hp <= 0:
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int) -> None:
        super().__init__()

        self.image = pygame.Surface((44, 34), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (240, 210, 80), self.image.get_rect(), border_radius=8)
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(self.rect.centerx, self.rect.centery)

        self.speed = 320
        self.sprint_multiplier = 1.5

        self.shoot_cooldown = 0.20
        self._shoot_timer = 0.0

        # dégâts de base du joueur
        self.bullet_damage = 1

    def update_timers(self, dt: float) -> None:
        if self._shoot_timer > 0:
            self._shoot_timer -= dt

    def handle_movement(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)

        # ZQSD (AZERTY)
        if keys[pygame.K_q]:
            move.x -= 1
        if keys[pygame.K_d]:
            move.x += 1
        if keys[pygame.K_z]:
            move.y -= 1
        if keys[pygame.K_s]:
            move.y += 1

        # Flèches en déplacement (optionnel)
        if keys[pygame.K_LEFT]:
            move.x -= 1
        if keys[pygame.K_RIGHT]:
            move.x += 1
        if keys[pygame.K_UP]:
            move.y -= 1
        if keys[pygame.K_DOWN]:
            move.y += 1

        if move.length_squared() > 0:
            move = move.normalize()

        sprint = 1.0
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            sprint = self.sprint_multiplier

        self.pos += move * self.speed * sprint * dt

        half_w = self.rect.width / 2
        half_h = self.rect.height / 2
        self.pos.x = max(half_w, min(WIDTH - half_w, self.pos.x))
        self.pos.y = max(half_h, min(HEIGHT - half_h, self.pos.y))

        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def get_shoot_direction(self) -> pygame.Vector2:
        keys = pygame.key.get_pressed()
        shoot = pygame.Vector2(0, 0)

        # Tir UNIQUEMENT IJKL
        if keys[pygame.K_j]:
            shoot.x -= 1
        if keys[pygame.K_l]:
            shoot.x += 1
        if keys[pygame.K_i]:
            shoot.y -= 1
        if keys[pygame.K_k]:
            shoot.y += 1

        if shoot.length_squared() > 0:
            shoot = shoot.normalize()

        return shoot

    def shoot(self) -> Bullet | None:
        if self._shoot_timer > 0:
            return None

        direction = self.get_shoot_direction()
        if direction.length_squared() == 0:
            return None

        self._shoot_timer = self.shoot_cooldown
        b = Bullet(self.rect.centerx, self.rect.centery, direction)
        b.damage = self.bullet_damage
        return b
