from pettingzoo import ParallelEnv
from gymnasium.spaces import Box, Discrete
import pygame
import numpy as np

from src.starfighter_game import StarfighterGame
import src.consts as CONSTANTS

class StarfighterEnv(ParallelEnv):
    metadata = {
        "name": "starfighter_env",
        "render_modes": ["human"],
        "is_parallelizable": True,
        "render_fps": 60
    }

    def __init__(self, render_mode):
        self.render_mode = render_mode

        self.num_red = CONSTANTS.RED_TEAM_SIZE
        self.num_blue = CONSTANTS.BLUE_TEAM_SIZE

        self.agents = []
        
        for i in range(self.num_red):
            self.agents.append(f"Red_{i}")

        for i in range(self.num_blue):
            self.agents.append(f"Blue_{i}")

        self.num_agents = self.num_red + self.num_blue

        self.max_ships = self.num_agents
        self.max_projectiles = self.num_agents * 2 # can be this because based on missile speed and range in relation to weapon timeout, all set in consts.py, each fighter can have only <2> missile(s) on the map at a time
        self.max_objects = self.max_ships + self.max_projectiles

        shape = ([self.max_objects + 1, 4 + 5]) # 4 for typemask, 5 for positions/directions
        obs_space = Box(low=-1.0, high=1.0, shape=shape, dtype=np.float64)
        self.observation_spaces = dict(
            zip(
                self.agents,
                [obs_space for _ in enumerate(self.agents)]
            )
        )

        self.action_spaces = dict(
            zip(self.agents, [[Discrete(2), Discrete(3), Discrete(3)] for _ in enumerate(self.agents)]) # first is for forward, second is for rotating, third is for firing/reloading
        )

        if self.render_mode == "human":
            self.clock = pygame.time.Clock()

    def reinit(self):
        self.game = StarfighterGame(self.num_red, self.num_blue)

        if self.render_mode is not None:
            self.render()

    def reset(self, seed=None, options=None):


        self.reinit()

    def step(self, actions):
        self.game.tick(actions)

        if self.render_mode is not None:
            self.render()

    def render(self):
        if self.screen is None:
            pygame.init()
            self.screen = pygame.display.set_mode((CONSTANTS.MAP_WIDTH, CONSTANTS.MAP_HEIGHT))
            pygame.display.set_caption("Starfighter")

        self.screen.fill((0,0,0))
        self.game.ship_sprites.draw(self.screen)
        self.game.projectile_sprites.draw(self.screen)

        pygame.display.update()
        self.clock.tick(self.metadata["render_fps"])

    def observation_space(self, agent):
        return self.observation_spaces[agent]

    def action_space(self, agent):
        return self.action_spaces[agent]
