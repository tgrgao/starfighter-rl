import pygame

from src.starfighter_game import StarfighterGame
from src.consts import FighterActions

game = StarfighterGame(10, 10)

action_mapping = {
    pygame.K_w : FighterActions.FORWARD,
    pygame.K_a : FighterActions.TURN_CCW,
    pygame.K_d : FighterActions.TURN_CW,
    pygame.K_SPACE : FighterActions.FIRE,
    pygame.K_r : FighterActions.RELOAD
}

clock = pygame.time.Clock()

actions = []
while(True):
    actions = [action for action in actions if action == FighterActions.FORWARD or action == FighterActions.TURN_CCW or action == FighterActions.TURN_CW]
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key in action_mapping.keys():
                actions.append(action_mapping[event.key])
        if event.type == pygame.KEYUP:
            if event.key in action_mapping.keys():
                if action_mapping[event.key] in actions:
                    actions.remove(action_mapping[event.key])
    
    game.tick({"Red_1": actions})
    clock.tick(30)
        