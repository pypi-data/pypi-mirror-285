from .env import VectorVelocityEnv
from .game.game import Game

def test_with_random_moves(episodes=10):
    """
    Test the VectorVelocity environment with random moves
    :param episodes: int: number of episodes to run
    """

    for episode in range(episodes):
        env = VectorVelocityEnv("human")
        reset = env.reset()
        done = False
        while not done:
            action = env.action_space.sample()
            obs, rewards, done, _, info = env.step(action)
            env.render()
            if done:
                print(f"Episode {episode} ended with reward: {rewards}")
    env.close()

def play_as_human(sound_volume:float=0.0, save_volume:bool=False):
    """
    starting the VectorVeclcity game and makes it playable by the user
    :param sound_volume: float: audio volume between 0.0 and 1.0
    :param save_volume: bool: save the volume setting
    """
    game = Game("human")

    if sound_volume:
        game.assetMgr.set_audio_volume(sound_volume, save_volume)

    game.run()
