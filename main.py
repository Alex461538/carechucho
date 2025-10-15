"""Main module for the project."""

import pygame

SCREEN_WIDTH = 720
SCREEN_HEIGHT = 720

# pygame setup
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED)
clock = pygame.time.Clock()

from universe import Universe
from input import InputManager, MouseButtonState

def main():
    """
    Main loop for the project.
    """
    input_manager = InputManager(SCREEN_WIDTH, SCREEN_HEIGHT)

    universe = Universe(SCREEN_WIDTH, SCREEN_HEIGHT)
    universe.graph_from_file("Constellations.json")

    running = True
    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEWHEEL:
                input_manager.on_mouse_wheel(event)
        
        input_manager.update()
        universe.update()

        if input_manager.mouse_scroll.y != 0:
            universe.zoom(input_manager.mouse_scroll.y * 0.3, input_manager.mouse_position)

        if input_manager.mouse_buttons[1] == MouseButtonState.DOWN:
            universe.translate( input_manager.mouse_movement.x, -input_manager.mouse_movement.y )

        # fill the screen with a color to wipe away anything from last frame
        screen.fill((0, 0, 0))

        universe.draw(screen)

        # flip() the display to put your work on screen
        pygame.display.flip()
        # limits FPS to framerate
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()