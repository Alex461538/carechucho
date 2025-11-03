"""Main module for the project."""

import pygame
import time
import math

SCREEN_WIDTH = 720
SCREEN_HEIGHT = 720

# pygame setup
pygame.init()
pygame.mixer.init()
pygame.font.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED)
clock = pygame.time.Clock()

import res
from universe import Universe
from input import InputManager, MouseButtonState
from traversal import Traversal

""" 
TODO IMPORTANT:
    Modificar el core del traversal para manejar los datos requeridos

2.0 Animar ruta
1.2 traversal a partir de condiciones
0.8 Carga de archivo en interfaz
0.5 Bloqueo de caminos
"""

def main():
    """
    Main loop for the project.
    """
    input_manager = InputManager(SCREEN_WIDTH, SCREEN_HEIGHT)

    universe = Universe(SCREEN_WIDTH, SCREEN_HEIGHT)

    stats = universe.graph_from_file("Constellations.json")

    traversal = Traversal(universe.graph, stats)

    running = True
    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEWHEEL:
                input_manager.on_mouse_wheel(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_g and not traversal.playing:
                    traversal.use_grass = not traversal.use_grass
                    traversal.calculate()
                if event.key == pygame.K_i and not traversal.playing:
                    traversal.use_investigative_labors = not traversal.use_investigative_labors
                    traversal.calculate()
                if event.key == pygame.K_p:
                    if traversal.playing:
                        traversal.stop()
                    else:
                        traversal.play()
        
        input_manager.update()
        universe.update()

        if input_manager.mouse_scroll.y != 0:
            universe.zoom(input_manager.mouse_scroll.y * 0.3, input_manager.mouse_position)

        if input_manager.mouse_buttons[1] == MouseButtonState.DOWN or input_manager.mouse_buttons[0] == MouseButtonState.DOWN:
            universe.translate( input_manager.mouse_movement.x, -input_manager.mouse_movement.y )

        # fill the screen with a color to wipe away anything from last frame
        screen.fill( res.Color.BACKGROUND.value )

        traversal.update(universe)

        traversal.draw(screen)

        hovered_star, hovered_edge = universe.draw(screen)

        traversal.draw_donkey(screen)

        if not traversal.playing:
            if hovered_edge:
                if input_manager.mouse_buttons[0] == MouseButtonState.PRESSED:
                    universe.graph.lock_edge(hovered_edge[0], hovered_edge[1])
                    traversal.calculate()

            if hovered_star:
                text_image = res.Font.NJ.value.render(f"{hovered_star.name}", False, (255, 255, 255), (0,0,0))
                screen.blit(text_image, ( input_manager.mouse_position.x, input_manager.mouse_position.y - text_image.get_size()[1] ) )

                if input_manager.mouse_buttons[0] == MouseButtonState.PRESSED:
                    print(f"Clicked on star: {hovered_star.name} (ID: {hovered_star.id}) in constellations: {', '.join(hovered_star.constellations)}")

                    traversal.set_origin(hovered_star)
        
        unactive_color = (0,0,0)
        active_color = (0, 50 + 20 * math.sin( time.time() * 5 ), 40)

        text_image = res.Font.NJ.value.render(f"[P]: Playing traversal", False, (255, 255, 255), active_color if traversal.playing else unactive_color)
        screen.blit(text_image, ( 0, SCREEN_HEIGHT - text_image.get_size()[1] * 6) )

        if traversal.playing:
            unactive_color = (20,20,20)
            active_color = (40, 40, 40)
        
        text_image = res.Font.NJ.value.render(f"{traversal.stats}", False, (255, 255, 255), (0,0,0,0))
        screen.blit(text_image, ( 0, SCREEN_HEIGHT - text_image.get_size()[1]) )
        text_image = res.Font.NJ.value.render(f"[G]: Use grass", False, (255, 255, 255), active_color if traversal.use_grass else unactive_color)
        screen.blit(text_image, ( 0, SCREEN_HEIGHT - text_image.get_size()[1] * 3) )
        text_image = res.Font.NJ.value.render(f"[I]: Use investigative labors", False, (255, 255, 255), active_color if traversal.use_investigative_labors else unactive_color)
        screen.blit(text_image, ( 0, SCREEN_HEIGHT - text_image.get_size()[1] * 4) )

        # flip() the display to put your work on screen
        pygame.display.flip()
        # limits FPS to framerate
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()