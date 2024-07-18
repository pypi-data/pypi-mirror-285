import pygame
from .obstacle import Obstacle
from .config.settings import LANE_POSITIONS


class Coin: 
    """
    Coin class to represent a coin object in the game.
    """
    def __init__(self, gameScreen, speed, y,  lane_x, id: int):
        self.x = lane_x
        self.lane = LANE_POSITIONS.index(lane_x)
        self.y = y
        self.speed = speed
        self.gameScreen = gameScreen
        self.id = id


    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, 10, 10)
    
    def update(self):
        """
        Update the position of the coin.
        """
        self.y += self.speed
    
    def is_off_screen(self):
        """
        Check if the coin is off the screen.
        """
        return self.y > self.gameScreen.get_height()
        
    def draw(self, gameScreen):
        """
        Draw the coin on the screen.
        """
        pygame.draw.circle(gameScreen, (235, 175, 4), (self.x, self.y), 8) 


