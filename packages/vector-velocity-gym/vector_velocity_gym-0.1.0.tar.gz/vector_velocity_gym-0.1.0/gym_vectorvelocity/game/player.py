import pygame
from .config import settings
from .asset_manager import AssetManager

class Player:
    """
    Player Controller class to represent the player object in the game.
    :param x: int, The x position of the player to start
    :param lane_positions: list, The list of lane positions
    :param assetMgr: The asset manager object.
    """
    def __init__(self, x: int, lane_positions: list, assetMgr: AssetManager):
        self.image = assetMgr.get_asset("player")
        self.lane_positions = lane_positions
        self.target_lane = 1
        self.current_lane = 1
        self.x = x
        self.y = settings.PLAYER_Y
        self.speed = 1350

    @property
    def rect(self):
        return self.image.get_rect(topleft=(self.x, self.y))

    def update(self, dt):
        target_x = self.lane_positions[self.target_lane]
        if self.x != target_x:
            step = self.speed * dt
            distance = target_x - self.x

            if abs(distance) > step:
                self.x += step * (distance / abs(distance))
            else:
                self.x = target_x
                self.current_lane = self.target_lane

    def move_left(self):
        """
        Move the player to the left lane.
        """
        if self.current_lane > 0:
            self.target_lane = self.current_lane - 1

    def move_right(self):
        """
        Move the player to the right lane.
        """
        if self.current_lane < len(self.lane_positions) - 1:
            self.target_lane = self.current_lane + 1

    def stay_in_lane(self):
        """
        Keep the player in the current lane.
        """
        self.target_lane = self.current_lane

    def draw(self, screen):
        """
        Draw the player on the screen.
        """
        screen.blit(self.image, (self.x, self.y))
    
    def get_current_positon(self):
        """
        Get the current position of the player.
        """
        return settings.LANE_POSITIONS[self.current_lane]
    
    def update_speed(self, speed):
        """
        Update the speed of the player.
        """
        self.speed += speed