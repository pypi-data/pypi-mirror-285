import pygame
from .obstacle import Obstacle
from .coin import Coin
import random
from .player import Player
from .level_area import LevelArea
from .config import settings 
from .asset_manager import AssetManager

class SpawnManager: 
    """
    SpawnManager class to manage the spawning and moving of objects inside the game.
    :param player: The player object.
    :param gameScreen: The game screen object.
    :param setGameOver: The function to set the game over state.
    :param lane_positions: list, The list of lane positions.
    :param speed: float, The speed of the objects.
    :param assetMgr: The asset manager object.
    :param seed: int, The seed for the random number generator.
    """

    def __init__(self, player: Player, gameScreen, setGameOver, lane_positions: list, speed, assetMgr: AssetManager, seed: int = 42):
        self.gameScreen = gameScreen
        self.player = player
        self.lane_positions = lane_positions
        self.obstacles = []
        self.used_lanes = []
        self.coins = []
        self.obstacle_spawn_timer = 0
        self.coin_spawn_timer = 0
        self.obstacle_spawn_rate = 2.5
        self.speed = speed
        self.coin_spawn_rate = self.obstacle_spawn_rate +2
        self.level = LevelArea(gameScreen)
        self.set_game_over = setGameOver
        self.assetMgr = assetMgr
        self.next_obstacle_id = 0
        self.next_coin_id = 0
        random.seed(seed)


    def __spawn_level(self):
        """
        Spawn the level area.
        """
        self.level.draw()

    def update_spawn_rates(self):
        """
        Update the spawn rates of the obstacles and coins.
        """
        if self.obstacle_spawn_rate >= settings.MAINIMUM_OBSTACLE_SPAWN_RATE:
            self.obstacle_spawn_rate -= settings.OBSTACLE_SPAWN_RATE_DECREASE
            self.coin_spawn_rate = (self.obstacle_spawn_rate + 2) * settings.COIN_SPAWN_RATE_MULTIPLIER


    def __get_available_lane(self):
        """
        Get an available lane to spawn an object.
        """
        available_lanes = [lane for lane in self.lane_positions if lane not in self.used_lanes]
        if not available_lanes:
            return None
        return random.choice(available_lanes)


    def update_speed(self, speed: float):
        """
        Update the speed of the objects.
        :param speed: float, The new speed of the objects.
        """
        self.speed = speed
        for obstacle in self.obstacles:
            obstacle.speed = speed
        for coin in self.coins:
            coin.speed = speed


    def check_collisions(self, source: any, objects: list, updateCoins = False):
        """
        Check for collisions between the source object and the list of objects.
        :param source: The source object.
        :param objects: The list of objects to check for collisions.
        """
        try: 
            for object in objects:
                if source.rect.colliderect(object.rect):
                    if isinstance(object, Coin):
                        self.coins.remove(object)
                        if updateCoins: updateCoins(1)
                    elif isinstance(object, Obstacle):
                        if pygame.rect.Rect.contains(object.rect, source.rect):
                            self.coins.remove(source)   
                            continue
                        if isinstance(source, Player):   
                            self.set_game_over()         
        except Exception as e:
            return

            
    def spawn_obstacles(self):
        count = random.randint(1, settings.MAXIMUM_OBSTACLE_SPAWN_COUNT)
        spawned = []
        y_offset = -100
        lane = self.__get_available_lane()

        for _ in range(count):    
            x_offset = random.randint(-82, 83)
            if lane is None:
                return
            obstacle_id = self.next_obstacle_id
            obstacle = Obstacle(self.gameScreen, self.speed, lane, y_offset, x_offset, self.assetMgr, obstacle_id)

            y_offset -= settings.OBSTACLE_Y_OFFSET_DECREASE
            spawned.append(obstacle)
            self.obstacles.append(obstacle)
            self.next_obstacle_id += 1
            self.used_lanes.append(lane)


    def spawn_coins(self):
        spawn_count = random.randint(5, 10)
        lane_count = random.randint(1, 2)
        current_lane_player = self.player.current_lane
        roi = self.lane_positions.copy()
        roi.pop(current_lane_player)        
        y = -110

        for _ in range(lane_count):
            for i in range(spawn_count):
                coin_id = self.next_coin_id
                coin = Coin(self.gameScreen, self.speed, y, roi[_], coin_id)
                self.coins.append(coin)
                self.next_coin_id += 1
                y -= settings.COIN_Y_OFFSET_DECREASE


    def __remove_objects(self, objects):
        for object in objects:
            object.update()
            if object.is_off_screen():
                objects.remove(object)
                if isinstance(object, Obstacle):
                    self.used_lanes.pop()


    def update(self, dt):
        for coin in self.coins:
            if len(self.obstacles) == 0:
                break
            self.check_collisions(coin, self.obstacles)

        self.obstacle_spawn_timer += dt
        self.coin_spawn_timer += dt

        if self.obstacle_spawn_timer >= self.obstacle_spawn_rate:
            self.obstacle_spawn_timer = 0
            self.spawn_obstacles()

        if self.coin_spawn_timer >= self.coin_spawn_rate:
            self.coin_spawn_timer = 0
            self.spawn_coins()

        self.__remove_objects(self.obstacles)
        self.__remove_objects(self.coins)


    def draw(self):
        self.__spawn_level()
        self.player.draw(self.gameScreen)
        for obstacle in self.obstacles:
            obstacle.draw(self.gameScreen)
        
        for coin in self.coins:
            coin.draw(self.gameScreen)
        

