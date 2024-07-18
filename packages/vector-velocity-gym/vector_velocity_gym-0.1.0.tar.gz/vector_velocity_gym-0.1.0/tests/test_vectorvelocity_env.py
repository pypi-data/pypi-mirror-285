import unittest
import numpy as np
from gym_vectorvelocity.env import VectorVelocityEnv
from gym_vectorvelocity.game.config.settings import MAXIMUM_SPEED

class TestVectorVelocityEnv(unittest.TestCase):
    
    def setUp(self):
        self.env = VectorVelocityEnv(mode='agent')

    def test_env_initialization(self):
        """
        Test the environment initialization
        """
        self.assertIsNotNone(self.env)
        self.assertEqual(self.env.mode, 'agent')

    def test_reset(self):
        """
        Test the reset functionality
        """
        obs, info = self.env.reset()
        self.assertIsNotNone(obs)
        self.assertIsInstance(obs, dict)
        self.check_observation_space(obs)

    def test_step(self):
        """
        Test stepping through the environment
        each step one time
        """
        for step in range(3):
            self.env.reset()
            obs, reward, done, truncated, info = self.env.step(step)
            self.assertIsInstance(obs, dict)
            self.assertIsInstance(reward, float)
            self.assertIsInstance(done, bool)
            self.assertIsInstance(truncated, bool)
            self.check_observation_space(obs)

    def test_action_space(self):
        """
        Test if the action space is correctly defined
        """
        self.assertEqual(self.env.action_space.n, 3)

    def test_observation_space(self):
        """
        Test if the observation space is correctly defined
        """
        obs_space = self.env.observation_space.spaces
        self.assertIn("obstacles", obs_space)
        self.assertIn("coins", obs_space)
        self.assertIn("obstacle_dists", obs_space)
        self.assertIn("coin_dists", obs_space)
        self.assertIn("lane_obstacles", obs_space)
        self.assertIn("lane_coins", obs_space)
        self.assertIn("score", obs_space)
        self.assertIn("collected_coins", obs_space)
        self.assertIn("speed", obs_space)
        self.assertIn("player_pos", obs_space)

    def check_observation_space(self, obs):
        """
        Helper function to check if the observation is valid
        """
        self.assertIn("obstacles", obs)
        self.assertIn("coins", obs)
        self.assertIn("obstacle_dists", obs)
        self.assertIn("coin_dists", obs)
        self.assertIn("lane_obstacles", obs)
        self.assertIn("lane_coins", obs)
        self.assertIn("score", obs)
        self.assertIn("collected_coins", obs)
        self.assertIn("speed", obs)
        self.assertIn("player_pos", obs)

        self.assertIsInstance(obs["obstacles"], np.ndarray)
        self.assertEqual(obs["obstacles"].shape, (self.env.NUM_MAX_OBSTACLES * 2,))
        self.assertTrue((obs["obstacles"] >= -1).all() and (obs["obstacles"] <= 1).all())

        self.assertIsInstance(obs["coins"], np.ndarray)
        self.assertEqual(obs["coins"].shape, (self.env.NUM_MAX_COINS * 2,))
        self.assertTrue((obs["coins"] >= -1).all() and (obs["coins"] <= 1).all())

        self.assertIsInstance(obs["obstacle_dists"], np.ndarray)
        self.assertEqual(obs["obstacle_dists"].shape, (self.env.NUM_MAX_OBSTACLES * 2,))
        self.assertTrue((obs["obstacle_dists"] >= -1).all() and (obs["obstacle_dists"] <= 1).all())

        self.assertIsInstance(obs["coin_dists"], np.ndarray)
        self.assertEqual(obs["coin_dists"].shape, (self.env.NUM_MAX_COINS * 2,))
        self.assertTrue((obs["coin_dists"] >= -1).all() and (obs["coin_dists"] <= 1).all())

        self.assertIsInstance(obs["lane_obstacles"], np.ndarray)
        self.assertEqual(obs["lane_obstacles"].shape, (self.env.NUM_MAX_OBSTACLES,))
        self.assertTrue((obs["lane_obstacles"] >= 0).all() and (obs["lane_obstacles"] <= self.env.NUM_LANES).all())

        self.assertIsInstance(obs["lane_coins"], np.ndarray)
        self.assertEqual(obs["lane_coins"].shape, (self.env.NUM_MAX_COINS,))
        self.assertTrue((obs["lane_coins"] >= 0).all() and (obs["lane_coins"] <= self.env.NUM_LANES).all())

        self.assertIsInstance(obs["score"], int)
        self.assertGreaterEqual(obs["score"], 0)
        self.assertLessEqual(obs["score"], 120000)

        self.assertIsInstance(obs["collected_coins"], int)
        self.assertGreaterEqual(obs["collected_coins"], 0)
        self.assertLessEqual(obs["collected_coins"], 20000)

        self.assertIsInstance(obs["speed"], int)
        self.assertGreaterEqual(obs["speed"], 0)
        self.assertLessEqual(obs["speed"], MAXIMUM_SPEED)

        self.assertIsInstance(obs["player_pos"], np.ndarray)
        self.assertEqual(obs["player_pos"].shape, (1,))
        self.assertTrue((obs["player_pos"] >= 0).all() and (obs["player_pos"] <= 1).all())

    def test_random_moves(self):
        """
        Test the environment by running random moves for multiple episodes
        """
        episodes = 10
        for _ in range(episodes):
            obs, info = self.env.reset()
            done = False
            while not done:
                action = self.env.action_space.sample()
                obs, reward, done, truncated, info = self.env.step(action)
                self.assertIsInstance(obs, dict)
                self.assertIsInstance(reward, float)
                self.assertIsInstance(done, bool)
                self.assertIsInstance(truncated, bool)
                self.check_observation_space(obs)

if __name__ == '__main__':
    unittest.main()
