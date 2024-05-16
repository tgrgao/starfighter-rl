import pygame

from src.fighter import Fighter
from src.missile import Missile
import src.consts as CONSTANTS

class StarfighterGame():

    def __init__(self, num_red, num_blue):
        self.agents = {}

        self.ship_sprites = pygame.sprite.Group()
        self.red_sprites = pygame.sprite.Group()
        self.blue_sprites = pygame.sprite.Group()
        self.projectile_sprites = pygame.sprite.Group()
        
        red_starting_pos = pygame.Vector2(100, 100)
        red_starting_angle = 180
        for i in range(num_red):
            agent_name = f"Red_{i}"
            self.agents[agent_name] = Fighter(0, agent_name, red_starting_pos, red_starting_angle)
            self.ship_sprites.add(self.agents[agent_name])
            self.red_sprites.add(self.agents[agent_name])
            red_starting_pos.x += 50

        blue_starting_pos = pygame.Vector2(900, 900)
        blue_starting_angle = 0
        for i in range(num_blue):
            agent_name = f"Blue_{i}"
            self.agents[agent_name] = Fighter(1, f"Blue_{i}", blue_starting_pos, blue_starting_angle)
            self.ship_sprites.add(self.agents[agent_name])
            self.blue_sprites.add(self.agents[agent_name])
            blue_starting_pos.x -= 50

        self.events = {}

    def tick(self, actions):
        self.events = {
            "victory": [],
            "kills": [],
            "ship_collisions": [],
            "out_of_bounds": [] 
        }

        for agent_name, action_list in actions.items():
            agent_sprite = self.agents[agent_name]
            if not agent_sprite.alive:
                continue
            agent_sprite.tick(action_list)
            if agent_sprite.out_of_bounds:
                self.events["out_of_bounds"].append((agent_sprite.agent_name))
                agent_sprite.alive = False
                agent_sprite.kill()

        # Check for inter-ship collisions
        collisions = pygame.sprite.groupcollide(self.ship_sprites, self.ship_sprites, False, False)
        for k,v in collisions.items():
            for sprite in v:
                if k != sprite:
                    if (sprite.alive):
                        self.events["ship_collisions"].append((k.agent_name, v.agent_name))
                        sprite.alive = False
                        sprite.kill()

        for agent_sprite in self.agents.values():
            if agent_sprite.missile_launched:
                agent_sprite.missile_launched = 0
                self.projectile_sprites.add(Missile(agent_name, agent_sprite.pos, agent_sprite.angle))

        for projectile in self.projectile_sprites:
            projectile.tick()
            if projectile.out_of_bounds:
                projectile.alive = False
                projectile.kill()

        # Check for ship-projectile collisions
        collisions = pygame.sprite.groupcollide(self.projectile_sprites, self.ship_sprites, False, False)
        for k,v in collisions.items():
            if (len(v) > 0 and k.alive):
                k.alive = False
                k.kill()
            for sprite in v:
                if k != sprite:
                    if (sprite.alive):
                        self.events["kills"].append((k.owner, v.agent_name))
                        sprite.alive = False
                        sprite.kill()

        if (not self.red_sprites.has() and not self.blue_sprites.has()):
            self.events["victory"].append(-1)

        if (not self.blue_sprites.has()):
            self.events["victory"].append(0)

        if (not self.red_sprites.has()):
            self.events["victory"].append(1)