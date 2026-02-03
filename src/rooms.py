# progression -- salle 1 -> salle 2 -> salle 3 -> salle 4 -> boss.
#  condition de victoire c’est “survivre X secondes
# Plus tard on peut faire “tuer N ennemis”, mais là on veut du solide.

from __future__ import annotations
import pygame
from dataclasses import dataclass
from .settings import ROOM_COUNT, ROOM_DURATION_SEC, ITEMS_ORDER


@dataclass
class RoomResult:
    success: bool
    gained_item: str | None = None


class RoomManager:
    def __init__(self) -> None:
        self.room_index = 1  # 1..4
        self.items: list[str] = []
        self._room_start_ms = pygame.time.get_ticks()

    def reset_run(self) -> None:
        """Reset quand on relance une partie."""
        self.room_index = 1
        self.items = []
        self._room_start_ms = pygame.time.get_ticks()

    def start_room(self) -> None:
        """Lancé au début de chaque salle."""
        self._room_start_ms = pygame.time.get_ticks()

    def time_left_sec(self) -> int:
        """Temps restant pour valider la salle (en secondes)."""
        elapsed_ms = pygame.time.get_ticks() - self._room_start_ms
        elapsed_sec = elapsed_ms // 1000
        return max(0, ROOM_DURATION_SEC - int(elapsed_sec))

    def is_room_cleared(self) -> bool:
        """Salle validée si le timer est à 0."""
        return self.time_left_sec() == 0

    def clear_room(self) -> RoomResult:
        """
        On passe à la salle suivante + on donne l’item correspondant.
        Important: l’item est “logique” (pas besoin de sprites).
        """
        gained = None

        # Don d’item si on a un item prévu
        if 1 <= self.room_index <= len(ITEMS_ORDER):
            gained = ITEMS_ORDER[self.room_index - 1]
            self.items.append(gained)

        # Si on n’est pas à la dernière salle-- on avance
        if self.room_index < ROOM_COUNT:
            self.room_index += 1
            self.start_room()
            return RoomResult(success=True, gained_item=gained)

        # Sinon, salle 4 validée -> fin des salles, le jeu va aller au boss
        return RoomResult(success=True, gained_item=gained)

    def is_last_room(self) -> bool:
        return self.room_index == ROOM_COUNT
