import pygame
import math

import src.consts as CONSTANTS

class Missile(pygame.sprite.Sprite):

    def __init__(self, owner, pos, angle):
        super().__init__()
        self.owner = owner

        self.org_image = pygame.image.load("assets/Missile.png")
        self.angle = angle
        self.curr_pos = pos
        self.org_pos = pos
        self.direction = pygame.Vector2(0, -1).rotate(-self.angle)

        self.image = pygame.transform.rotate(self.org_image, self.angle)

        self.rect = self.image.get_rect(center=pos)

        self.speed = CONSTANTS.MISSILE_SPEED
        self.range = CONSTANTS.MISSILE_RANGE

        self.out_of_bounds = False
        self.alive = True

    def tick(self):
        move_angle = math.radians(self.angle+90)
        self.rect.x += math.cos(move_angle) * self.speed
        self.rect.y -= math.sin(move_angle) * self.speed
        self.curr_pos = pygame.Vector2(self.rect.center)
        if (self.rect.x < 10 or self.rect.x > CONSTANTS.MAP_WIDTH - 10 or self.rect.y < 10 or self.rect.y > CONSTANTS.MAP_HEIGHT - 10) or (self.curr_pos.distance_to(self.org_pos) > self.range):
            self.out_of_bounds = True

        