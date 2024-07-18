
from .game.config.settings import FRAME_RATE, SCREEN_HEIGHT, LANE_POSITIONS, MAXIMUM_SPEED, PLAYER_Y, LEVEL_WIDTH
from .game.game import Game
import gymnasium as gym
from gymnasium import spaces
import numpy as np
import time 

class VectorVelocityEnv(gym.Env):
    metadata = {'render_modes': ['human'], 'render_fps': FRAME_RATE}

    def __init__(self, mode='agent', seed=42):
        """
        Initialize the VectorVelocity gym environment
        :param mode: str: 'human' or 'agent' mode
        - 'human' mode: the environment is rendered
        - 'agent' mode: the environment is not rendered

        Note: The environment can not be rendered in jupyter notebooks or colabs
        """

        # init environment
        super(VectorVelocityEnv, self).__init__()
        self.mode = mode
        self.seed = seed

        self.game = Game(self.mode, seed=seed)

        # init constant vakues
        self._init_constants()

        # init observation and action spaces
        self._init_spaces()

        # rewards and penaltys related variables
        self.start_time = time.time()
        self.current_reward = 0
        self.dodged_obstacles = set()
        self.missed_coins = set()
        self.latest_speed = self.game.speed

        # reard and penalty values
        self.game_over_penalty = 75
        self.coin_missed_penalty = 1

        self.dodged_obstacle_reward = 2
        self.coin_reward = 3


    def _init_spaces(self):
        """
        Initialize the observation and action spaces

        Observation space:
        - obstacles: normalized x and y coordinates of the obstacles
        - coins: normalized x and y coordinates of the coins
        - obstacle_dists: normalized x and y distances of the obstacles
        - coin_dists: normalized x and y distances of the coins
        - lane_obstacles: lane of the obstacles (0 if no obstacle)
        - lane_coins: lane of the coins (0 if no coin)
        - score: current score of the player (capped to 120000)
        - collected_coins: number of collected coins (capped to 20000)
        - speed: current speed of the game (capped to MAXIMUM_SPEED of game settings)
        - player_pos: normalized x coordinate of the player

        Action space:
        - 0: Do nothing
        - 1: Move right
        - 2: Move left
        """

        # observation space definition
        self.observation_space = spaces.Dict({
            "obstacles": spaces.Box(low=-1, high=1, shape=(self.NUM_MAX_OBSTACLES*2,), dtype=np.float32),
            "coins": spaces.Box(low=-1, high=1, shape=(self.NUM_MAX_COINS*2,), dtype=np.float32),
            "obstacle_dists": spaces.Box(low=-1, high=1, shape=(self.NUM_MAX_OBSTACLES*2,), dtype=np.float32),
            "coin_dists": spaces.Box(low=-1, high=1, shape=(self.NUM_MAX_COINS*2,), dtype=np.float32),
            "lane_obstacles": spaces.MultiDiscrete([self.NUM_LANES +1]*self.NUM_MAX_OBSTACLES ,dtype=np.int32),
            "lane_coins": spaces.MultiDiscrete([self.NUM_LANES +1]*self.NUM_MAX_COINS, dtype=np.int32),
            "score": spaces.Discrete(120000 +1),
            "collected_coins": spaces.Discrete(20000 +1),
            "speed": spaces.Discrete(MAXIMUM_SPEED +1),
            "player_pos": spaces.Box(low=0, high=1, shape=(1,), dtype=np.float32)
        })

        # action space definition
        self.action_space = spaces.Discrete(3)


    def _init_constants(self):
        """
        Initialize the constants used for normalizing and constructing the observation values
        """
        self.OBSTACLE_Y_CONDITION = -89
        self.COIN_Y_CONDITION = -19
        self.OBSTACLE_MIN_X = LANE_POSITIONS[0] - 82
        self.OBSTACLE_MAX_X = LANE_POSITIONS[-1] + 83
        self.MAX_Y_DISTANCE = np.sqrt(LEVEL_WIDTH**2 + SCREEN_HEIGHT**2)
        self.NUM_LANES = len(LANE_POSITIONS)
        self.NUM_MAX_OBSTACLES = 9
        self.NUM_MAX_COINS = 20


    def __normalize_obstacle_coordinate(self, value: tuple):
        """
        Normalize the x and y coordinates of an obstacle
        """
        norm_x = (value[0] - self.OBSTACLE_MIN_X) / (self.OBSTACLE_MAX_X - self.OBSTACLE_MIN_X)
        norm_y = (value[1] + abs(self.OBSTACLE_Y_CONDITION)) / (SCREEN_HEIGHT + abs(self.OBSTACLE_Y_CONDITION))
        return norm_x, norm_y
    

    def __normalize_coin_coordinate(self, value: tuple):
        """
        Normalize the x and y coordinates of a coin
        """
        norm_x = (value[0] - LANE_POSITIONS[0]) / (LANE_POSITIONS[-1] - LANE_POSITIONS[0])
        norm_y = (value[1] + abs(self.COIN_Y_CONDITION)) / (SCREEN_HEIGHT + abs(self.COIN_Y_CONDITION))
        return norm_x, norm_y
    

    def __normalize_player_coordinate(self, value: tuple):
        """
        Normalize the x coordinate of the player
        """
        norm_x = (value[0] - LANE_POSITIONS[0]) / (LANE_POSITIONS[-1] - LANE_POSITIONS[0])
        norm_y = PLAYER_Y / SCREEN_HEIGHT
        return norm_x, norm_y

        
    def __normalize_distance(self, x, y):
        """
        Normalize the x and y distance
        """
        norm_x = x / LEVEL_WIDTH
        norm_y = y / self.MAX_Y_DISTANCE

        return norm_x, norm_y
        
    def __calculate_normalized_distance(self, player_pos, object_pos):
        """
        Calculate the normalized x and y distance between the player and an object
        """
        player_x, player_y = player_pos
        object_x, object_y = object_pos

        x_dist = player_x - object_x
        y_dist = player_y - object_y

        x_dist, y_dist = self.__normalize_distance(x_dist, y_dist)

        return x_dist, y_dist
         
    def reset(self, seed=None):
        super().reset(seed=seed) 
        self.current_reward = 0
        self.dodged_obstacles = set()
        self.missed_coins = set()
        self.latest_speed = self.game.speed
        self.start_time = time.time()

        self.game.restart()

        return self._get_observation(), {}

    def step(self, action):
        if action == 0: # Do nothing
            self.game.player.stay_in_lane()
        elif action == 1:  # Move right
            self.game.player.move_right()
        elif action == 2: # move left
            self.game.player.move_left()

        self.game.update(self.game.clock.tick(FRAME_RATE) / 1000.0) 
        observation = self._get_observation()
        reward = self._get_reward()
        done = self.game.is_game_over()

        truncated = False

        return observation, reward, done, truncated, {}

    def _get_observation(self):
        # get player position and normalize it
        player_pos = (self.game.player.get_current_positon(), PLAYER_Y)
        player_x = self.__normalize_player_coordinate(player_pos)[0]
        player_x = np.array([player_x], dtype=np.float32)

        # retrieve score, speed and collected coins
        score = int(self.game.score)
        speed = int(self.game.speed)
        collected_coins = self.game.collected_coins
        
        # init obstacle and coin related variables to an array of -1
        obstacles = np.full((self.NUM_MAX_OBSTACLES*2, ), -1, dtype=np.float32)
        coins = np.full((self.NUM_MAX_COINS*2, ), -1, dtype=np.float32)
        obstacles_lane = np.full((self.NUM_MAX_OBSTACLES, ), 0, dtype=np.int32)
        coins_lane = np.full((self.NUM_MAX_COINS, ), 0, dtype=np.int32)

        obstacles_dists = np.full((self.NUM_MAX_OBSTACLES*2, ), -1, dtype=np.float32)
        coin_dists = np.full((self.NUM_MAX_COINS*2, ), -1, dtype=np.float32)

        # fill the obstacle related arrays with the normalized values for existing obstacles
        for index, obstacle in enumerate(self.game.spawnMgr.obstacles):
            if index >= self.NUM_MAX_OBSTACLES: 
                break
            if obstacle.y < self.OBSTACLE_Y_CONDITION:
                continue
            norm_x, norm_y = self.__normalize_obstacle_coordinate((obstacle.x, obstacle.y))
            obstacles[index] = norm_x
            obstacles[index +1] = norm_y

            # get the original lane of the obstacle by removing the offset
            init_spawn_point = obstacle.x - obstacle.x_offset
            lane = LANE_POSITIONS.index(init_spawn_point) +1 # add 1 because 0 is reserved for the case where there is no obstacle
            obstacles_lane[index] = lane

            # calculate the normalized distance between the player and the obstacle
            x_dist, y_dist = self.__calculate_normalized_distance(player_pos, (obstacle.x, obstacle.y))
            obstacles_dists[index] = x_dist
            obstacles_dists[index +1] = y_dist

        # fill the coin related arrays with the normalized values for existing coins
        for index, coin in enumerate(self.game.spawnMgr.coins):
            if index >= self.NUM_MAX_COINS:
                break
            if coin.y < self.COIN_Y_CONDITION:
                continue
            norm_x, norm_y = self.__normalize_coin_coordinate((coin.x, coin.y))
            coins[index] = norm_x
            coins[index +1] = norm_y

            lane = LANE_POSITIONS.index(coin.x) +1 # add 1 because 0 is reserved for the case where there is no coin
            coins_lane[index] = lane

            x_dist, y_dist = self.__calculate_normalized_distance(player_pos, (coin.x, coin.y))
            coin_dists[index] = x_dist
            coin_dists[index +1] = y_dist

        # construct the observation dictionary
        observation = {
            "obstacles": obstacles,
            "coins": coins,
            "obstacle_dists": obstacles_dists,
            "coin_dists": coin_dists,
            "lane_obstacles": obstacles_lane,
            "lane_coins": coins_lane,
            "score": score,
            "collected_coins": collected_coins,
            "speed": speed,
            "player_pos": player_x
        }

        return observation
    

    def normalize_reward(self, reward):
        return reward / 10
    
    
    def _calculate_dodged_obstacle_reward(self, speed_factor):
        """
        Calculate the reward for dodging obstacles.
        dodged obstacle is an obstacle that has passed the player without colliding
        """
        reward = 0

        current_obstacles = {(obstacle.id, obstacle.y) for obstacle in self.game.spawnMgr.obstacles}
        dodged_obstacles = {obstacle_id for obstacle_id, y in current_obstacles if y >= (self.game.player.y + 100)}

        new_dodged_obstacles = dodged_obstacles - self.dodged_obstacles

        self.dodged_obstacles.update(new_dodged_obstacles)

        self.dodged_obstacles.intersection_update({obstacle_id for obstacle_id, _ in current_obstacles})

        reward += len(new_dodged_obstacles) * self.dodged_obstacle_reward * speed_factor

        return reward

    def _calculate_missed_coin_penalty(self, speed_factor: float):
        """
        Calculate the penalty for missing coins. 
        missed coin is a coin that has passed the player without being collected
        :param speed_factor: float: the speed factor of the game
        """
        reward = 0

        current_coins = {(coin.id, coin.y) for coin in self.game.spawnMgr.coins}
        missed_coins = {coin_id for coin_id, y in current_coins if y >= (self.game.player.y + 20)}

        new_missed_coins = missed_coins - self.missed_coins

        self.missed_coins.update(new_missed_coins)

        self.missed_coins.intersection_update({coin_id for coin_id, _ in current_coins})

        reward -= len(new_missed_coins) * self.coin_missed_penalty * speed_factor

        return reward
       
    
    def _calculate_collected_coin_reward(self, speed_factor: float):
        """
        Calculate the reward for collecting coins
        :param speed_factor: float: the speed factor of the game
        """
        reward = 0
        if self.game.collected_coins > self.game.last_updated_coins:
            reward += self.coin_reward * speed_factor
            self.game.last_updated_coins = self.game.collected_coins

        return reward
    
    def _calculate_time_reward(self):
        """
        Calculate the reward for surviving
        """
        reward = 0
        current_time = time.time()
        time_elapsed = current_time - self.start_time
        reward += time_elapsed * 0.1

        return reward

    def _get_reward(self):
        """
        Calculate the reward for the current step
        - time reward: small reward for surviving
        - dodged obstacle reward: reward for dodging obstacles
        - missed coin penalty: penalty for missing coins
        - collected coin reward: reward for collecting coins
        - game over penalty: penalty for game over
        """

        reward = self.current_reward
        speed_factor = self.game.speed / 4 

        if self.game.is_game_over():
            reward -= self.game_over_penalty * speed_factor
            self.current_reward = reward
            return reward
        
        reward += self._calculate_time_reward()
        reward += self._calculate_dodged_obstacle_reward(speed_factor)
        reward += self._calculate_missed_coin_penalty(speed_factor)
        reward += self._calculate_collected_coin_reward(speed_factor)

        reward = self.normalize_reward(reward)
                             
        self.current_reward = reward

        return reward
    
    def render(self):
        self.game.render()

    def close(self):
        self.game.quit()
        super().close()