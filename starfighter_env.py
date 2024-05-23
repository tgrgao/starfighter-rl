from pettingzoo import ParallelEnv
from gymnasium.spaces import Box, MultiDiscrete
import pygame
import numpy as np

from src.starfighter_game import StarfighterGame
import src.consts as CONSTANTS
from src.consts import FighterActions

REWARDS = {
    "victory": 100,
    "defeat": -100,
    "stalemate": -50,
    "killed_enemy" : 10,
    "killed_by_enemy" : 10,
    "killed_friendly" : -50,
    "killed_by_friendly" : -10,
    "collision_enemy": 0,
    "collision_friendly" : -20,
    "out_of_bounds": -50
}

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

        self.possible_agents = []
        
        for i in range(self.num_red):
            self.possible_agents.append(f"Red_{i}")

        for i in range(self.num_blue):
            self.possible_agents.append(f"Blue_{i}")

        self.agents = self.possible_agents[:]

        self.max_ships = self.num_agents
        self.max_projectiles = self.num_agents * 2 # can be this because based on missile speed and range in relation to weapon timeout, all set in consts.py, each fighter can have only <2> missile(s) on the map at a time
        self.max_objects = self.max_ships + self.max_projectiles

        self.vector_width = 4 + 4 + 1 # 4 for typemask, 4 for positions/directions, 1 for distance to agent
        shape = ([self.max_objects + 1, self.vector_width]) 
        obs_space = Box(low=-1.0, high=1.0, shape=shape, dtype=np.float64)
        self.observation_spaces = dict(
            zip(
                self.possible_agents,
                [obs_space for _ in enumerate(self.possible_agents)]
            )
        )

        self.action_spaces = dict(
            zip(self.possible_agents, [MultiDiscrete(np.array([2, 3, 3])) for _ in enumerate(self.possible_agents)]) # first is for forward, second is for rotating, third is for firing/reloading
        )

        if self.render_mode == "human":
            self.clock = pygame.time.Clock()

    def reset(self, seed=None, options=None):
        self.agents = self.possible_agents[:]
        self.alive_agents = self.agents[:]
        self.rewards = dict(zip(self.agents, [0 for _ in self.agents]))
        self.terminations = dict(zip(self.agents, [False for _ in self.agents]))
        self.truncations = dict(zip(self.agents, [False for _ in self.agents]))
        self.infos = dict(zip(self.agents, [{} for _ in self.agents]))

        self.game = StarfighterGame(self.num_red, self.num_blue)

        self.done = False

        if self.render_mode is not None:
            self.render()

    def step(self, actions):
        for agent_name, action_vector in actions:
            action_list = []
            if action_vector[0] == 1:
                action_list.append(FighterActions.FORWARD)
            if action_vector[1] == -1:
                action_list.append(FighterActions.TURN_CCW)
            elif action_vector[1] == 1:
                action_list.append(FighterActions.TURN_CW)
            if action_vector[2] == -1:
                action_list.append(FighterActions.FIRE)
            if action_vector[2] == 1:
                action_list.append(FighterActions.RELOAD)
            actions[agent_name] = action_list

        self.game.tick(actions)

        for agent in self.rewards:
            self.rewards[agent] = 0
        for (killer, killed) in self.game.events["kills"]:
            if self.game.agents[killer].team != self.game.agents[killed].team:
                self.rewards[killer] += REWARDS["killed_enemy"]
                self.rewards[killed] += REWARDS["killed_by_enemy"]
            else:
                self.rewards[killer] += REWARDS["killed_friendly"]
                self.rewards[killed] += REWARDS["killed_by_friendly"]
            self.terminations[killed] = True
        for (collider_1, collider_2) in self.game.events["ship_collisions"]:
            if self.game.agents[collider_1].team != self.game.agents[collider_2].team:
                self.rewards[collider_1] += REWARDS["collision_enemy"]
                self.rewards[collider_2] += REWARDS["collision_enemy"]
            else:
                self.rewards[collider_1] += REWARDS["collision_friendly"]
                self.rewards[collider_2] += REWARDS["collision_friendly"]
            self.terminations[collider_1] = True
            self.terminations[collider_2] = True
        for (killed) in self.game.events["out_of_bounds"]:
            self.rewards[killed] += REWARDS["out_of_bounds"]
            self.terminations[killed] = True

        if (len(self.game.events["victory"]) > 0):
            if (self.game.events["victory"][0] == -1):
                for agent_name in self.game.ship_sprites:
                    self.rewards[agent_name] += REWARDS["stalemate"]
            if (self.game.events["victory"][0] == 0):
                for agent in self.game.red_sprites:
                    self.rewards[agent.agent_name] += REWARDS["victory"]
                for agent in self.game.blue_sprites:
                    self.rewards[agent.agent_name] += REWARDS["defeat"]
            if (self.game.events["victory"][0] == 1):
                for agent in self.game.blue_sprites:
                    self.rewards[agent.agent_name] += REWARDS["victory"]
                for agent in self.game.red_sprites:
                    self.rewards[agent.agent_name] += REWARDS["defeat"]
            self.done = True

        if self.render_mode is not None:
            self.render()

        self.observations = {}
        vector_state = self.get_vector_state()
        state = vector_state[:, -4:]
        all_ids = vector_state[:, :-4]
        all_pos = state[:, 0:2]
        all_ang = state[:, 2:4]
        for i in range(self.num_agents):
            agent_state = vector_state[i].copy()
            agent_state[0] = 1
            agent_state[1] = 0
            agent_state[2] = 0
            agent_pos = np.expand_dims(agent_state[-4:-2], axis=0)
            agent_state = np.append(agent_state, [0])

            rel_pos = all_pos - agent_pos
            norm_pos = np.linalg.norm(rel_pos, axis=1, keepdims=True) / np.sqrt(2)
            all_state = np.concatenate([all_ids, rel_pos, all_ang, norm_pos], axis=-1)

            agent_state = np.expand_dims(agent_state, axis=0)
            self.observations[self.possible_agents[i]] = np.concatenate([agent_state, all_state], axis=0)

        

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
    
    def get_vector_state(self):
        state = []
        for agent_name in self.possible_agents:
            agent_vector = np.zeros(self.vector_width)
            if not self.terminations[agent_name]:
                agent = self.game.ship_sprites[agent_name]
                if agent.team == 0:
                    agent_vector[1] = 1
                else:
                    agent_vector[2] = 1
                agent_vector[4] = agent.rect.x / CONSTANTS.MAP_WIDTH
                agent_vector[5] = agent.rect.y / CONSTANTS.MAP_HEIGHT
                agent_vector[6] = agent.direction[0]
                agent_vector[7] = agent.direction[1]
            state.append(agent_vector)

        for projectile in self.game.projectile_sprites:
            projectile_vector = np.zeros(self.vector_width)
            projectile_vector[3] = 1
            projectile_vector[4] = projectile.rect.x / CONSTANTS.MAP_WIDTH
            projectile_vector[5] = projectile.rect.y / CONSTANTS.MAP_HEIGHT
            projectile_vector[6] = projectile.direction[0]
            projectile_vector[7] = projectile.direction[1]
        
        return np.stack(state, axis=0)
