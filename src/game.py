#boucle principale.
# Elle ne fait pas le gameplay elle délègue aux scènes.

from __future__ import annotations
import pygame

from .settings import WIDTH, HEIGHT, FPS, TITLE, STARTING_HP
from .rooms import RoomManager
from .scenes import MenuScene, Scene


class Game:
    def __init__(self) -> None:
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        # Infos de run (réinitialisées quand on recommence)
        self.hp = STARTING_HP
        self.score = 0
        self.room_manager = RoomManager()

        # On démarre sur le menu
        self.scene: Scene = MenuScene(self)

    def start_new_run(self) -> None:
        """Reset de la partie."""
        self.hp = STARTING_HP
        self.score = 0
        self.room_manager.reset_run()

    def change_scene(self, new_scene: Scene) -> None:
        """Changement d’écran."""
        self.scene = new_scene

    def run(self) -> None:
        """Boucle principale."""
        # (Debug) Tu peux laisser ça pour vérifier que ça tourne
        # print("GAME LOOP START")

        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # dt en secondes

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.scene.handle_event(event)

            # (Debug) Voir la scène active
            # print("CURRENT SCENE:", type(self.scene).__name__)

            self.scene.update(dt)
            self.scene.render(self.screen)

            pygame.display.flip()

        pygame.quit()
