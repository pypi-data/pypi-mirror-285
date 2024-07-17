# VectorVelocity

<div align="center">
    <img src="https://github.com/MrChriwo/VectorVelocity/assets/96289753/66ee0ba9-0f26-4e11-b93d-6bcb097525b4" alt="VectorVelocity" width="65%">
</div>

[![Documentation](https://img.shields.io/badge/docs-online-green.svg)](https://MrChriwo.github.io/VectorVelocity/)
![Python Version](https://img.shields.io/badge/python-3.9%20|%203.10%20|%203.11%20|%203.12-blue.svg)

# Table of Contents

- [🙋‍♂️ Introduction](#introduction)
- [🎮 Game Description](#game-description)
    - [Third Party Assets](#third-party-assets)
- [🤖 RL Agent](#rl-agent)
    - [Problem Domain](#problem-domain)
    - [Agents](#agents)


# Introduction 

VectorVelocity is a challenging and engaging space-themed game created using Pygame, where a spaceship navigates through lanes, collecting coins and dodging descending asteroids. This project not only offers entertainment but also serves as a problem domain for a Reinforcement Learning (RL) agent. The core of this project is the development of an RL agent that learns to master the game, implemented in an OpenAI Gym environment tailored specifically for this game.

# Game Description 

In VectorVelocity, the player controls a spaceship moving across three lanes. The objective is to collect as many coins as possible while avoiding collisions with asteroids that move from the top of the screen to the bottom. As the game progresses, the speed increases, making the game increasingly difficult.

# Third Party Assets

This game was enriched significantly by incorporating various third-party assets. We are immensely grateful to the creators of these assets for making their work available and enhancing the gaming experience.

1. **Game Background**: The thematic space background, enhancing the visual appeal of our game, was sourced from [Vecteezy](https://www.vecteezy.com).
2. **Space Ship**: The spaceship, which players navigate through asteroids, was created by FoozleCC as part of the Void Pack. Explore more of FoozleCC's creations [here](https://www.youtube.com/@FoozleCC/videos).
3. **Background Music**: The atmospheric tunes from Goose Ninjas' Space Music Pack set the perfect mood for our adventures through space. Check out more of Goose Ninjas' music on their [Itch.io page](https://gooseninja.itch.io/).

We extend a huge thanks to the mentioned authors for making their work freely available.


# RL Agent

## Problem Domain 
The challenge for the RL agent in VectorVelocity is to learn optimal strategies for maximizing the score by skillfully collecting coins while avoiding asteroids. The agent is required to make decisions in real-time, adjusting to the game's increasing speed and the randomness of asteroid placements. Additionally, some coins spawn between asteroids in positions that may not always be reachable, adding a layer of decision-making complexity. This requires the player, and consequently the RL agent, to assess whether pursuing a coin is worth the risk of potential collision. This problem domain provides a rich and challenging environment for exploring and refining reinforcement learning techniques.


## Agents 

We have decided to use the Proximal Policy Optimization (PPO) algorithm to train an agent within our environment. PPO, a reinforcement learning algorithm developed by OpenAI, is known for its robustness and efficiency in learning policies for various types of environments.

### Sample Agent Development

For those interested in seeing a practical implementation or experimenting with the agent development process, sample agent development can be found in the `lab` branch of this repository. This branch includes experimental features and developmental progress on new agent strategies.

To access and contribute to the ongoing agent development, switch to the `lab` branch:
