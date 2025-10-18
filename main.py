"""Main module for the project."""

import pygame

SCREEN_WIDTH = 720
SCREEN_HEIGHT = 720

# pygame setup
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED)
clock = pygame.time.Clock()

import res
from universe import Universe
from input import InputManager, MouseButtonState
from traversal import Traversal

def main():
    """
    Main loop for the project.
    """
    input_manager = InputManager(SCREEN_WIDTH, SCREEN_HEIGHT)

    universe = Universe(SCREEN_WIDTH, SCREEN_HEIGHT)
    universe.graph_from_file("Constellations.json")

    traversal = Traversal(universe.graph)

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

        if input_manager.mouse_buttons[1] == MouseButtonState.DOWN or input_manager.mouse_buttons[0] == MouseButtonState.DOWN:
            universe.translate( input_manager.mouse_movement.x, -input_manager.mouse_movement.y )

        # fill the screen with a color to wipe away anything from last frame
        screen.fill( res.Color.BACKGROUND.value )

        traversal.follow_universe(universe)

        traversal.draw(screen)

        hovered_star, hovered_edge = universe.draw(screen)

        traversal.draw_donkey(screen)

        if hovered_edge:
            if input_manager.mouse_buttons[0] == MouseButtonState.PRESSED:
                universe.graph.lock_edge(hovered_edge[0], hovered_edge[1])

        if hovered_star:
            text_image = res.Font.NJ.value.render(f"{hovered_star.name}", False, (255, 255, 255), (0,0,0))
            screen.blit(text_image, ( input_manager.mouse_position.x, input_manager.mouse_position.y - text_image.get_size()[1] ) )

            if input_manager.mouse_buttons[0] == MouseButtonState.PRESSED:
                print(f"Clicked on star: {hovered_star.name} (ID: {hovered_star.id}) in constellations: {', '.join(hovered_star.constellations)}")

                traversal.set_origin(hovered_star)

        # flip() the display to put your work on screen
        pygame.display.flip()
        # limits FPS to framerate
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()