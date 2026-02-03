# Progresion
# Combat 1 Item room -> Combat 2 -> Item room -> Combat 3 -> Item room -> Combat 4 (BOSS SEUL) -> Victory

from __future__ import annotations
import pygame

from .settings import ROOM_COUNT, ITEMS_ORDER
from .rooms import RoomManager
from .player import Player
from .enemy_dummy import EnemyDummy


# -------------- réglages difficulté --------------
BASE_ROOM_TIME = 20          # salle 1 = 20s
TIME_DECREASE_PER_ROOM = 3   # -3s à chaque salle
MIN_ROOM_TIME = 8            # minimum 8s


class Scene:
    def __init__(self, game: "Game") -> None:
        self.game = game

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def render(self, screen: pygame.Surface) -> None:
        pass


class MenuScene(Scene):
    def __init__(self, game: "Game") -> None:
        super().__init__(game)
        pygame.font.init()
        self.font = pygame.font.SysFont("consolas", 26)
        self.big = pygame.font.SysFont("consolas", 52)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.game.start_new_run()
            self.game.change_scene(CombatRoomScene(self.game))

    def render(self, screen: pygame.Surface) -> None:
        screen.fill((15, 15, 25))
        title = self.big.render("Tacos vs Kebab", True, (240, 240, 240))
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 150))
        screen.blit(self.font.render("ESPACE pour commencer", True, (180, 180, 180)),
                    (screen.get_width() // 2 - 160, 260))
        screen.blit(self.font.render("ZQSD bouger | ESPACE attaquer", True, (160, 160, 160)),
                    (screen.get_width() // 2 - 210, 300))


# ------------------ BOSS ------------------
class Boss(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, hp: int = 40) -> None:
        super().__init__()
        self.max_hp = hp
        self.hp = hp

        size = 120
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (170, 80, 60), self.image.get_rect(), border_radius=18)
        pygame.draw.rect(self.image, (30, 30, 30), self.image.get_rect(), 3, border_radius=18)

        self.rect = self.image.get_rect(center=(x, y))

    def take_damage(self, amount: int) -> None:
        self.hp -= amount
        if self.hp <= 0:
            self.kill()


class CombatRoomScene(Scene):
    def __init__(self, game: "Game") -> None:
        super().__init__(game)
        pygame.font.init()
        self.font = pygame.font.SysFont("consolas", 20)

        self.room_manager: RoomManager = self.game.room_manager

        # timer qui diminue selon la salle
        room_i = self.room_manager.room_index  # 1..4 normalement
        self.room_time = max(MIN_ROOM_TIME, BASE_ROOM_TIME - (room_i - 1) * TIME_DECREASE_PER_ROOM)
        self.start_ms = pygame.time.get_ticks()

        self.player = Player(480, 270)
        self.player_group = pygame.sprite.Group(self.player)

        # IMPORTANT: pour pas multi-hit pendant 0.12s
        # on reset à chaque appui qui lance une attaque
        self.hit_this_attack: set[int] = set()

        # Spawn ennemis selon salle
        self.enemies = pygame.sprite.Group()

        if self.room_manager.room_index < ROOM_COUNT:
            # salles 1-3 : ennemis "normaux"
            # plus tu avances, plus ils ont de HP
            bonus = (self.room_manager.room_index - 1) * 2  # +2 hp par salle

            self.enemies.add(
                EnemyDummy(220, 180, hp=4 + bonus, size=42),
                EnemyDummy(720, 200, hp=6 + bonus, size=52),
                EnemyDummy(520, 380, hp=8 + bonus, size=64),
            )
        else:
            # salle 4 : boss seul
            self.enemies.add(Boss(640, 260, hp=40))

        # Invincibilité joueur si contact boss (option simple)
        self.player_iframes = 0.0
        self.iframe_duration = 0.6

    def time_left(self) -> int:
        elapsed = (pygame.time.get_ticks() - self.start_ms) // 1000
        left = int(self.room_time - elapsed)
        return max(0, left)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.change_scene(MenuScene(self.game))

            if event.key == pygame.K_SPACE:
                started = self.player.start_attack()
                if started:
                    # reset des ennemis touchés pour CETTE attaque
                    self.hit_this_attack.clear()

    def update(self, dt: float) -> None:
        self.player.update_timers(dt)
        self.player.handle_movement(dt)

        if self.player_iframes > 0:
            self.player_iframes -= dt
            if self.player_iframes < 0:
                self.player_iframes = 0

        # ----------- attaque: 1 hit par ennemi par appui -----------
        if self.player.is_attacking():
            atk = self.player.get_attack_rect()

            for enemy in list(self.enemies):
                if enemy.rect.colliderect(atk):
                    # id() pour identifier l'objet en mémoire
                    eid = id(enemy)
                    if eid not in self.hit_this_attack:
                        enemy.take_damage(self.player.attack_damage)
                        self.hit_this_attack.add(eid)

                        # Score si un ennemi normal meurt
                        if hasattr(enemy, "max_hp") and not isinstance(enemy, Boss):
                            if getattr(enemy, "hp", 1) <= 0:
                                self.game.score += 1

        #                       contact boss = dégâts joueur
        for enemy in self.enemies:
            if isinstance(enemy, Boss):
                if self.player_iframes <= 0 and self.player.rect.colliderect(enemy.rect):
                    self.game.hp -= 1
                    self.player_iframes = self.iframe_duration

        # Game over
        if self.game.hp <= 0:
            self.game.change_scene(GameOverScene(self.game))
            return

        #                                           fin de salle
        # Salles 1-3 -- fin quand timer fini
        # Salle 4 (boss)*-- fin quand boss mort
        if self.room_manager.room_index < ROOM_COUNT:
            if self.time_left() <= 0:
                idx = self.room_manager.room_index - 1
                self.game.pending_item = ITEMS_ORDER[idx] if 0 <= idx < len(ITEMS_ORDER) else "item_mystere"
                self.game.change_scene(ItemRoomScene(self.game))
        else:
            # boss mort -- victory
            boss_alive = any(isinstance(e, Boss) for e in self.enemies.sprites())
            if not boss_alive:
                self.game.change_scene(VictoryScene(self.game))

    def render(self, screen: pygame.Surface) -> None:
        screen.fill((18, 18, 24))

        # HUD
        screen.blit(self.font.render(f"Salle: {self.room_manager.room_index}/{ROOM_COUNT}", True, (220, 220, 220)), (12, 12))
        screen.blit(self.font.render(f"HP Joueur: {self.game.hp}", True, (220, 220, 220)), (12, 36))

        if self.room_manager.room_index < ROOM_COUNT:
            screen.blit(self.font.render(f"Temps: {self.time_left()}s / {self.room_time}s", True, (240, 210, 80)), (12, 60))
        else:
            # boss hp
            boss = next((e for e in self.enemies.sprites() if isinstance(e, Boss)), None)
            if boss:
                screen.blit(self.font.render(f"HP Boss: {boss.hp}/{boss.max_hp}", True, (240, 210, 80)), (12, 60))

        items = ", ".join(self.room_manager.items) if self.room_manager.items else "-"
        screen.blit(self.font.render(f"Items: {items}", True, (200, 200, 200)), (12, 84))

        screen.blit(self.font.render("ZQSD bouger | ESPACE taper", True, (150, 150, 150)), (12, 110))

        # affichage HP ennemis (debug clair)
        y = 140
        for i, e in enumerate(self.enemies.sprites(), start=1):
            if hasattr(e, "hp") and hasattr(e, "max_hp"):
                screen.blit(self.font.render(f"Enemy {i} HP: {e.hp}/{e.max_hp}", True, (180, 180, 180)), (12, y))
                y += 22

        # draw
        self.enemies.draw(screen)
        self.player_group.draw(screen)

        if self.player.is_attacking():
            pygame.draw.rect(screen, (255, 80, 80), self.player.get_attack_rect(), 2)

        if self.player_iframes > 0:
            pygame.draw.rect(screen, (240, 240, 240), self.player.rect.inflate(6, 6), 2)


class ItemRoomScene(Scene):
    def __init__(self, game: "Game") -> None:
        super().__init__(game)
        pygame.font.init()
        self.font = pygame.font.SysFont("consolas", 22)
        self.big = pygame.font.SysFont("consolas", 46)

        self.room_manager: RoomManager = self.game.room_manager

        self.player = Player(480, 360)
        self.player_group = pygame.sprite.Group(self.player)

        self.chest_rect = pygame.Rect(0, 0, 80, 60)
        self.chest_rect.center = (480, 240)

        self.item_name: str = getattr(self.game, "pending_item", "item_mystere")
        self.taken = False

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.change_scene(MenuScene(self.game))

            if event.key == pygame.K_RETURN and self.taken:
                # passer à la salle suivante
                self.room_manager.room_index += 1
                self.game.change_scene(CombatRoomScene(self.game))

    def update(self, dt: float) -> None:
        self.player.update_timers(dt)
        self.player.handle_movement(dt)

        keys = pygame.key.get_pressed()
        if self.player.rect.colliderect(self.chest_rect) and keys[pygame.K_e] and not self.taken:
            self.taken = True
            self.room_manager.items.append(self.item_name)
            self.game.pending_item = None

    def render(self, screen: pygame.Surface) -> None:
        screen.fill((14, 20, 18))

        title = self.big.render("Salle ITEM", True, (240, 240, 240))
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 60))

        pygame.draw.rect(screen, (200, 160, 60), self.chest_rect, border_radius=10)
        pygame.draw.rect(screen, (120, 90, 30), self.chest_rect, 3, border_radius=10)

        screen.blit(self.font.render(f"Item: {self.item_name}", True, (240, 210, 80)), (330, 140))

        if not self.taken:
            screen.blit(self.font.render("Va sur le coffre + E pour prendre", True, (200, 200, 200)), (180, 420))
        else:
            screen.blit(self.font.render("Pris ! ENTER pour continuer", True, (200, 200, 200)), (220, 420))

        self.player_group.draw(screen)


class GameOverScene(Scene):
    def __init__(self, game: "Game") -> None:
        super().__init__(game)
        pygame.font.init()
        self.font = pygame.font.SysFont("consolas", 28)
        self.big = pygame.font.SysFont("consolas", 56)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self.game.change_scene(MenuScene(self.game))

    def render(self, screen: pygame.Surface) -> None:
        screen.fill((8, 8, 10))
        title = self.big.render("GAME OVER", True, (240, 240, 240))
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 180))
        txt = self.font.render("R pour revenir au menu", True, (180, 180, 180))
        screen.blit(txt, (screen.get_width() // 2 - txt.get_width() // 2, 260))


class VictoryScene(Scene):
    def __init__(self, game: "Game") -> None:
        super().__init__(game)
        pygame.font.init()
        self.font = pygame.font.SysFont("consolas", 28)
        self.big = pygame.font.SysFont("consolas", 56)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self.game.change_scene(MenuScene(self.game))

    def render(self, screen: pygame.Surface) -> None:
        screen.fill((8, 18, 10))
        title = self.big.render("VICTOIRE", True, (240, 240, 240))
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 170))
        items = ", ".join(self.game.room_manager.items) if self.game.room_manager.items else "-"
        screen.blit(self.font.render(f"Items: {items}", True, (240, 210, 80)),
                    (screen.get_width() // 2 - 160, 260))
        screen.blit(self.font.render("R pour revenir au menu", True, (180, 180, 180)),
                    (screen.get_width() // 2 - 140, 330))
