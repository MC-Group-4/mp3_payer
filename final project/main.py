import pygame

pygame.init()
WIDTH, HEIGHT = 900, 500
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("First game")

WHITE = (255, 255, 255)
FPS = 60


def draw_window():
    SCREEN.fill(WHITE)
    # SCREEN.blit()
    pygame.display.update()


def main():
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        draw_window()
    pygame.quit()


if __name__ == "__main__":
    main()
