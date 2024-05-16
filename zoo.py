import pettingzoo
import pettingzoo.test

from starfighter_env import StarfighterEnv

env = StarfighterEnv(render_mode=None)

pettingzoo.test.parallel_api_test(env, num_cycles=100)