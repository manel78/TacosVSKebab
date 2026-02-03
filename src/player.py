# deplacement et gestion des touches pour le joueur
# ZQSD = bouger
# SHIFT = sprint
# ESPACE = attaquer

from __future__ import annotations
import pygame
from .settings import WIDTH, HEIGHT


class Player(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int) -> None:
        super().__init__()

        self.image = pygame.Surface((44, 34), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (240, 210, 80), self.image.get_rect(), border_radius=8)

        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(self.rect.centerx, self.rect.centery)

        # Mouvement
        self.speed = 320
        self.sprint_multiplier = 1.5

        # Direction où je "regarde"
        self.facing = pygame.Vector2(1, 0)

        # Attaque
        self.attack_damage = 1            # 1 coup = 1 dégât
        self.attack_range = 52
        self.attack_size = (56, 40)
        self.attack_active_time = 0.12
        self.attack_cooldown = 0.30

        self._attack_timer = 0.0
        self._attack_cd_timer = 0.0

    def update_timers(self, dt: float) -> None:
        if self._attack_timer > 0:
            self._attack_timer -= dt
            if self._attack_timer < 0:
                self._attack_timer = 0

        if self._attack_cd_timer > 0:
            self._attack_cd_timer -= dt
            if self._attack_cd_timer < 0:
                self._attack_cd_timer = 0

    def handle_movement(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)

        if keys[pygame.K_q]:
            move.x -= 1
        if keys[pygame.K_d]:
            move.x += 1
        if keys[pygame.K_z]:
            move.y -= 1
        if keys[pygame.K_s]:
            move.y += 1

        if move.length_squared() > 0:
            move = move.normalize()
            self.facing = pygame.Vector2(move.x, move.y)

        sprint = 1.0
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            sprint = self.sprint_multiplier

        self.pos += move * self.speed * sprint * dt

        # Clamp écran
        half_w = self.rect.width / 2
        half_h = self.rect.height / 2
        self.pos.x = max(half_w, min(WIDTH - half_w, self.pos.x))
        self.pos.y = max(half_h, min(HEIGHT - half_h, self.pos.y))

        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def can_attack(self) -> bool:
        return self._attack_cd_timer <= 0 and self._attack_timer <= 0

    def start_attack(self) -> bool:
        """Retourne True si l'attaque démarre vraiment (cooldown ok)."""
        if not self.can_attack():
            return False
        self._attack_timer = self.attack_active_time
        self._attack_cd_timer = self.attack_cooldown
        return True

    def is_attacking(self) -> bool:
        return self._attack_timer > 0

    def get_attack_rect(self) -> pygame.Rect:
        w, h = self.attack_size

        face = self.facing
        if face.length_squared() == 0:
            face = pygame.Vector2(1, 0)

        cx = self.rect.centerx + int(face.x * self.attack_range)
        cy = self.rect.centery + int(face.y * self.attack_range)

        r = pygame.Rect(0, 0, w, h)
        r.center = (cx, cy)
        return r
