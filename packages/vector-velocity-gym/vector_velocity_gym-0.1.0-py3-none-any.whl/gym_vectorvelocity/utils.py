from .env import VectorVelocityEnv
from .game.game import Game


def test_with_random_moves(episodes=5):
    """
    Test the VectorVelocity environment with random moves
    :param episodes: int: number of episodes to run

    NOTE: This function runs until all episodes are completed. It is recommended to run this function with a small number of episodes.
    Execute run in debug mode to manually stop the execution via debugger if needed.
    """
    env = VectorVelocityEnv("human")

    try:
        for episode in range(episodes):
            env.reset()
            done = False
            while not done:
                action = env.action_space.sample()
                obs, rewards, done, _, info = env.step(action)
                env.render()
                if done:
                    print(f"Episode {episode +1} ended with reward: {rewards}")
    finally:
        env.close()


def play_as_human(sound_volume: float | None = None, save_volume: bool = False):
    """
    starting the VectorVeclcity game and makes it playable by the user
    :param sound_volume: float: audio volume between 0.0 and 1.0
    :param save_volume: bool: save the volume setting
    """
    game = Game("human")

    if sound_volume is None:
        sound_volume = game.assetMgr.get_asset("bgmusic").get_volume()

    if sound_volume or sound_volume == 0:
        game.assetMgr.set_audio_volume(sound_volume, save_volume)

 
    game.run()


if __name__ == "__main__":
    test_with_random_moves()
    # play_as_human(sound_volume=0.5, save_volume=True)
