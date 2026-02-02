import pygame
from src.settings import WIDTH, HEIGHT, FPS


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tacos vs Kebab")

    clock = pygame.time.Clock()
    running = True

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((30, 30, 30))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
