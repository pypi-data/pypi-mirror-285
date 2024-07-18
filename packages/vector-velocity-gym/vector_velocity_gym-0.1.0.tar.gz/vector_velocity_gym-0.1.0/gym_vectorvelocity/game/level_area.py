import pygame
from .config import settings 
class LevelArea:
    """
    Represents the level area.
    """
    def __init__(self, screen):
        self.screen = screen
        self.rect = pygame.Rect(settings.LEVEL_X, settings.LEVEL_Y, settings.LEVEL_WIDTH, settings.LEVEL_HEIGHT)
        self.lane_positions = settings.LANE_POSITIONS

    def draw(self):
        # Creating a new surface with the same size as the rectangle
        transparent_surface = pygame.Surface((self.rect.width, self.rect.height))
        transparent_surface.set_alpha(115) 
        transparent_color = (0, 0, 0) 
        transparent_surface.fill(transparent_color)
        self.screen.blit(transparent_surface, (self.rect.x, self.rect.y))
       