# MIT License

# Copyright (c) 2024 Vindula Jayawardana, Baptiste Freydt, Ao Qu, Cameron Hickert, Zhongxia Yan, Cathy Wu

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse
from pathlib import Path


import numpy as np
from env.config import IntersectionZooEnvConfig
from env.task_context import PathTaskContext
from env.environment import IntersectionZooEnv
from sumo.constants import REGULAR

parser = argparse.ArgumentParser(description='Demo run arguments')
parser.add_argument('--dir', default='wd/new_exp', type=str, help='Result directory')
parser.add_argument('--intersection_dir', default='dataset/salt-lake-city', type=str, help='Path to intersection dataset')
parser.add_argument('--penetration', default=0.33, type=str, help='Eco drive adoption rate')
parser.add_argument('--temperature_humidity', default='68_46', type=str, help='Temperature and humidity for evaluations')

args = parser.parse_args()
print(args)

Path(args.dir).mkdir(parents=True, exist_ok=True)

tasks = PathTaskContext(
    dir=Path(args.intersection_dir),                    
    single_approach=True,
    penetration_rate=args.penetration,
    temperature_humidity=args.temperature_humidity,
    electric_or_regular=REGULAR,
)

env_conf = IntersectionZooEnvConfig(
    task_context=tasks.sample_task(),
    working_dir=Path(args.dir),
    moves_emissions_models=[args.temperature_humidity],
    fleet_reward_ratio=1,
    visualize_sumo=True,
)

# contexts = []
# for i in range(10):
#     print(i)
#     task = tasks.sample_task()
#     context = {
#         'intersection_dir': str(task.dir),
#         'single_approach': task.single_approach,
#         'penetration_rate': task.penetration_rate,
#         'temperature': int(task.temperature_humidity.split('_')[0]),
#         'humidity': int(task.temperature_humidity.split('_')[1]),
#         'electric_or_regular': task.electric_or_regular,
#         'compact_str': task.compact_str()
#     }
#     contexts.append(context)


# Create the environment
env = IntersectionZooEnv({"intersectionzoo_env_config": env_conf})

print("Environment variables:", env_conf.task_context)

def filter_obs(obs: dict):
    def simplify(v):
        if isinstance(v, np.ndarray):
            if len(v) == 1:
                return v[0]
            else:
                return v.tolist()
        else:
            return v

    return {k: {
        k2: simplify(v2) for k2, v2 in v.items() if k2 in ["speed", "relative_distance", "tl_phase"]
    } for k,v in obs.items() if k != "mock"}

def filter_rew(rew: dict):
    return {k: v for k,v in rew.items() if k != "mock"}

# Reset the environment
obs, _ = env.reset()
terminated = {"__all__": False}
while not terminated["__all__"]:
    # Send a constant action for all agents
    action = {agent: [1] for agent in obs.keys()}

    # Take a step in the environment
    obs, reward, terminated, truncated, info = env.step(action)

    # # Print the observations and reward
    # print("Observations:", filter_obs(obs))
    # print("Reward:", filter_rew(reward))

    for agent_id, agent_obs in obs.items():
        context_np = np.array([
            agent_obs["penetration_rate"],
            agent_obs["speed_limit"],
            agent_obs["green_phase"],
            agent_obs["red_phase"],
            agent_obs["temperature"],
            agent_obs["humidity"],
           np.array([agent_obs["electric"]], dtype=np.float32)
        ])
        print(
           
            # "penetration_rate:", agent_obs["penetration_rate"],
            # "lane_length:", agent_obs["lane_length"]
            # agent_obs["green_phase"], 
            # agent_obs["lane_index"]
            # agent_obs["electric"], 
            # np.shape(context_np),
            context_np  
        )

# Close the environment
env.close()
