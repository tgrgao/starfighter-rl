import pettingzoo
import pettingzoo.test

from starfighter_env import StarfighterEnv

env = StarfighterEnv(render_mode=None)
env.reset()

# pettingzoo.test.parallel_api_test(env, num_cycles=100)

i = 0
while env.agents:
    actions = {
        "Red_1": [1, 1, -1]
    }
    observations, rewards, terminations, truncations, infos = env.step(actions)
    print(observations["Red_1"])
    print(rewards)

    i += 1
    if i % 5 == 0:
        break

env.close()