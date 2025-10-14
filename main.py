"""Main module for the project."""

import pygame

SCREEN_WIDTH = 138
SCREEN_HEIGHT = 224

# pygame setup
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED)
clock = pygame.time.Clock()

def main():
    """
    Main loop for the project.
    """
    running = True
    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # fill the screen with a color to wipe away anything from last frame
        screen.fill((56, 0, 15))
        # flip() the display to put your work on screen
        pygame.display.flip()
        # limits FPS to framerate
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()