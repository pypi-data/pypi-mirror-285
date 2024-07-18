from .env import VectorVelocityEnv
from gymnasium import register


register(
    id='VectorVelocity-v0',
    entry_point='gym_vectorvelocity:VectorVelocityEnv',
)

__all__ = ['VectorVelocityEnv']
