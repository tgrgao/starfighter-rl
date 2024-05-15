import pygame

from src.fighter import Fighter
from src.missile import Missile

class StarfighterGame():

    def __init__(self, num_red, num_blue):
        pygame.init()

        WIDTH, HEIGHT = 1000, 1000
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Starfighter")

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

        self.ship_sprites.draw(self.screen)

        pygame.display.update()

    def tick(self, actions):
        for agent_name, action_list in actions.items():
            agent_sprite = self.agents[agent_name]
            if not agent_sprite.alive:
                continue
            agent_sprite.tick(action_list)
            if agent_sprite.out_of_bounds:
                agent_sprite.alive = False
                agent_sprite.kill()

        # Check for inter-ship collisions
        collisions = pygame.sprite.groupcollide(self.ship_sprites, self.ship_sprites, False, False)
        for k,v in collisions.items():
            for sprite in v:
                if k != sprite:
                    if (sprite.alive):
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
        collisions = pygame.sprite.groupcollide(self.ship_sprites, self.projectile_sprites, False, False)
        for k,v in collisions.items():
            if (len(v) > 0 and k.alive):
                k.alive = False
                k.kill()
            for sprite in v:
                if k != sprite:
                    if (sprite.alive):
                        sprite.alive = False
                        sprite.kill()

        self.screen.fill((0,0,0))
        self.ship_sprites.draw(self.screen)
        self.projectile_sprites.draw(self.screen)

        pygame.display.update()