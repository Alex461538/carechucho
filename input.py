import pygame
from pygame.math import Vector2

from enum import IntEnum

class MouseButtonState(IntEnum):
    UP = 0
    PRESSED = 1
    DOWN = 2
    RELEASED = 3

class InputManager:
    """
        An old & fancy input manager used in a js game.
    """
    def __init__(self, screen_width: float = 1, screen_height: float = 1):
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.mouse_scroll = Vector2(0, 0)
        self.mouse_scroll_hard = Vector2(0, 0)
        self.mouse_position = Vector2(0, 0)
        self.mouse_movement = Vector2(0, 0)
        self.mouse_movement_hard = Vector2(0, 0)
        self.normalized_mouse_position = Vector2(0, 0)
        
        self.mouse_press_position = [Vector2(0, 0) for _ in range(3)]
        self.mouse_down_position = [Vector2(0, 0) for _ in range(3)]
        self.mouse_release_position = [Vector2(0, 0) for _ in range(3)]
        self.mouse_drag = [Vector2(0, 0) for _ in range(3)]
        self.mouse_buttons = [MouseButtonState.UP for _ in range(3)]
        
        self._mouse_buttons_p = [False, False, False]
        self._mouse_position_p = Vector2(0, 0)
        self._mouse_wheel_a = False
        self.is_focused = False
    
    def get_bounding_rect(self):
        # Adapt this to return the actual bounds of your element
        # Example return format:
        return {
            'left': 0,
            'top': 0,
            'right': self.screen_width,
            'bottom': self.screen_height
        }
    
    def on_focus(self, e):
        self.is_focused = True
        self.on_mouse_down(e)
    
    def on_blur(self, e):
        self.is_focused = False
    
    def get_bounding_rect(self):
        # Adapt this to return the actual bounds of your element
        # Example return format:
        return {
            'left': 0,
            'top': 0,
            'right': 800,
            'bottom': 600
        }
    
    def on_mouse_wheel(self, event):
        self._mouse_wheel_a = 8
        # Adapt delta values based on your framework
        self.mouse_scroll_hard.x = event.x
        self.mouse_scroll_hard.y = event.y
    
    def get_mouse_buttons(self):
        def down(button):
            rect = self.get_bounding_rect()
            self.mouse_press_position[button] = Vector2(self.mouse_position.x - rect['left'], self.mouse_position.y - rect['top'])
            self._mouse_buttons_p[button] = True
        
        def up(button):
            rect = self.get_bounding_rect()
            self.mouse_release_position[button] = Vector2(self.mouse_position.x - rect['left'], self.mouse_position.y - rect['top'])
            self._mouse_buttons_p[button] = False
        
        mouse_buttons = pygame.mouse.get_pressed()

        if self._mouse_buttons_p[0] and not mouse_buttons[0]:
            up(0)
        elif not self._mouse_buttons_p[0] and mouse_buttons[0]:
            down(0)
        
        if self._mouse_buttons_p[1] and not mouse_buttons[1]:
            up(1)
        elif not self._mouse_buttons_p[1] and mouse_buttons[1]:
            down(1)
        
        if self._mouse_buttons_p[2] and not mouse_buttons[2]:
            up(2)
        elif not self._mouse_buttons_p[2] and mouse_buttons[2]:
            down(2)
    
    def get_mouse_position(self):
        # Get screen rect
        rect = self.get_bounding_rect()

        # Set mouse position
        self.mouse_position = Vector2(pygame.mouse.get_pos()[0] - rect['left'], pygame.mouse.get_pos()[1] - rect['top'])

        bounding_width = rect['right'] - rect['left']
        bounding_height = rect['bottom'] - rect['top']

        self.normalized_mouse_position = Vector2(
            self.mouse_position.x / bounding_width if bounding_width != 0 else 0,
            self.mouse_position.y / bounding_height if bounding_height != 0 else 0
        )

    def get_values_fron_pygame(self):
        self.get_mouse_position()
        self.get_mouse_buttons()
    
    def update(self):
        self.get_values_fron_pygame()

        for i in range(len(self.mouse_buttons)):
            if self._mouse_buttons_p[i]:
                self.mouse_buttons[i] = (
                    MouseButtonState.PRESSED if self.mouse_buttons[i] == MouseButtonState.UP
                    else MouseButtonState.DOWN
                )
            else:
                self.mouse_buttons[i] = (
                    MouseButtonState.RELEASED if self.mouse_buttons[i] == MouseButtonState.DOWN
                    else MouseButtonState.UP
                )
            
            if self.mouse_buttons[i] != MouseButtonState.UP:
                self.mouse_down_position[i] = Vector2(
                    self.mouse_position.x,
                    self.mouse_position.y
                )
                
                self.mouse_drag[i] = Vector2(
                    self.mouse_down_position[i].x - self.mouse_press_position[i].x,
                    self.mouse_down_position[i].y - self.mouse_press_position[i].y
                )
            else:
                self.mouse_drag[i] = Vector2(0, 0)
        
        if self._mouse_wheel_a > 0:
            self._mouse_wheel_a -= 1
        else:
            self.mouse_scroll_hard = Vector2(0, 0)
        
        damp = 0.2
        
        self.mouse_scroll.y = self.mouse_scroll.y * (1 - damp) + self.mouse_scroll_hard.y * damp
        
        self.mouse_movement.x = self.mouse_movement.x * (1 - damp) + self.mouse_movement_hard.x * damp
        self.mouse_movement.y = self.mouse_movement.y * (1 - damp) + self.mouse_movement_hard.y * damp
        
        self.mouse_movement_hard = Vector2(
            self.mouse_position.x - self._mouse_position_p.x,
            self.mouse_position.y - self._mouse_position_p.y
        )
        
        self._mouse_position_p = Vector2(self.mouse_position.x, self.mouse_position.y)