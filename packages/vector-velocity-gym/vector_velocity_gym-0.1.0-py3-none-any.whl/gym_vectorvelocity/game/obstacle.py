import pygame
import random
from .asset_manager import AssetManager
from .config.settings import LANE_POSITIONS
class Obstacle:
    """
    Obstacle class to represent an obstacle object in the game.
    :param gameScreen: The game screen object.
    :param speed: float, The speed of the obstacle.
    :param lane_x: int, The x position of the lane.
    :param y: int, The y position of the obstacle.
    :param x_offset: int, The x offset in pixels of the obstacle.
    :param assetMgr: The asset manager object.
    :param id: int, The id of the obstacle.
    """
    def __init__(self, gameScreen, speed: float, lane_x: int, y: int, x_offset: int, assetMgr: AssetManager, id: int):
        self.assetMgr = assetMgr
        self.x_offset = x_offset
        self.gameScreen = gameScreen
        self.width, self.height = 90, 90
        self.speed = speed
        self.y = y
        self.x = lane_x + x_offset
        self.lane = LANE_POSITIONS.index(lane_x)
        self.image = self.load_random_image()
        self.id = id

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    # loading random image from the asset manager
    def load_random_image(self):
        """
        Loads a random image from the asset managers list.
        """
        images = self.assetMgr.get_asset("obstacles")
        image = random.choice(images)
        image = pygame.transform.scale(image, (int(self.width), int(self.height)))
        return image
    
    def update(self):
        """
        Update the position of the obstacle.
        """
        self.y += self.speed

    def draw(self, screen):
        """
        Draw the obstacle on the screen.
        """
        screen.blit(self.image, (self.x, self.y))

    def is_off_screen(self):
        """
        Check if the obstacle is off the screen.
        """
        return self.y > self.gameScreen.get_height()