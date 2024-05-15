import pygame
import math

import src.consts as CONSTANTS
from src.consts import FighterActions

class Fighter(pygame.sprite.Sprite):

    def __init__(self, team, agent_name, pos, angle):
        super().__init__()
        self.agent_name = agent_name

        if (team == 0):
            self.org_image = pygame.image.load("assets/Red_Fighter.png")
        else:
            self.org_image = pygame.image.load("assets/Blue_Fighter.png")

        self.angle = angle
        self.pos = pos
        self.direction = pygame.Vector2(0, -1).rotate(-self.angle)

        self.image = pygame.transform.rotate(self.org_image, self.angle)

        self.rect = self.image.get_rect(center=pos)

        self.alive = True
        self.score = 0

        self.team = team

        self.forward_rate = CONSTANTS.FIGHTER_FORWARD_RATE
        self.angle_rate = CONSTANTS.FIGHTER_ANGLE_RATE

        self.weapon_timeout = CONSTANTS.FIGHTER_WEAPON_TIMEOUT
        self.curr_weapon_timeout = 0
        self.missile_launched = False

        self.magazine_size = CONSTANTS.FIGHTER_MAGAZINE_SIZE
        self.magazine = CONSTANTS.FIGHTER_MAGAZINE_SIZE
        self.reload_time = CONSTANTS.FIGHTER_RELOAD_TIME
        self.curr_reload_time = 0

        self.out_of_bounds = False

    def tick(self, actions):
        if (FighterActions.TURN_CCW in actions):
            self.angle += self.angle_rate
        if (FighterActions.TURN_CW in actions):
            self.angle -= self.angle_rate
        if (FighterActions.FORWARD in actions):
            move_angle = math.radians(self.angle+90)
            self.rect.x += math.cos(move_angle) * self.forward_rate
            self.rect.y -= math.sin(move_angle) * self.forward_rate

        self.direction = pygame.Vector2(0, -1).rotate(-self.angle)
        self.image = pygame.transform.rotate(self.org_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.pos = pygame.Vector2(self.rect.center)

        if (self.rect.x < 10 or self.rect.x > CONSTANTS.MAP_WIDTH - 10 or self.rect.y < 10 or self.rect.y > CONSTANTS.MAP_HEIGHT - 10):
            self.out_of_bounds = True

        if (FighterActions.FIRE in actions):
            if self.magazine > 0 and self.curr_weapon_timeout == 0 and self.curr_reload_time == 0:
                self.missile_launched = True
                self.magazine -= 1
                self.curr_weapon_timeout = self.weapon_timeout + 1
            else:
                self.missile_launched = False
        if (FighterActions.RELOAD in actions):
            if (self.curr_reload_time == 0):
                print("RELOAD")
                self.curr_reload_time = self.reload_time + 1

        if (self.curr_weapon_timeout > 0):
            self.curr_weapon_timeout -= 1
        
        if (self.curr_reload_time > 0):
            self.curr_reload_time -= 1
            if (self.curr_reload_time == 0):
                self.magazine = CONSTANTS.FIGHTER_MAGAZINE_SIZE