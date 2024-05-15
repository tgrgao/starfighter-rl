from pettingzoo import ParallelEnv
import pygame

from src.starfighter_game import StarfighterGame
import src.consts as CONSTANTS

class StarfighterEnv(ParallelEnv):
    metadata = {
        "name": "starfighter_env",
        "render_modes": ["human"],
        "is_parallelizable": True
    }

    def __init__(self):
        num_red = 10
        num_blue = 10

        self.agents = []
        self.num_agents = num_red + num_blue

        self.max_ships = self.num_agents
        self.max_projectiles = self.num_agents *  CONSTANTS.FIGHTER_MAGAZINE_SIZE   

        for i in range(num_red):
            self.agents.append(f"Red_{i}")

        for i in range(num_blue):
            self.agents.append(f"Blue_{i}")

        self.game = StarfighterGame(num_red, num_blue)


    def reset(self, seed=None, options=None):
        pass

    def step(self, actions):
        self.game.tick(actions)

    def render(self):
        pass

    def observation_space(self, agent):
        return self.observation_spaces[agent]

    def action_space(self, agent):
        return self.action_spaces[agent]
