import os
import argparse
from typing import Callable, Dict, List


import torch
from rlvortex.envs.base_env import EnvWrapper
from rlvortex.envs.gym_wrapper.gym_envs import (
    CartPole,
    LunarLander,
    MountainCarContinuous,
    Pendulum,
)


available_algs: List[str] = ["vpg", "a2c", "ppo"]
trained_model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trained_models")
trained_model_path_dict: Dict[str, Dict[str, str]] = {
    "cartpole": {"ppo": os.path.join(trained_model_path, "ppo_cartpole_500.pth")},
    "pendulum": {"ppo": os.path.join(trained_model_path, "ppo_pendulum_-133.pth")},
    "mountaincarc": {"ppo": os.path.join(trained_model_path, "ppo_mountaincarc_95.pth")},
    "lunarlander": {"ppo": os.path.join(trained_model_path, "ppo_lunarlander_300.pth")},
    "lunarlanderc": {"ppo": os.path.join(trained_model_path, "ppo_lunarlanderc_300.pth")},
}


available_env_dict: Dict[str, EnvWrapper] = {
    "cartpole": EnvWrapper(env=CartPole(num_envs=1, viz=True, device=torch.device("cpu"))),
    "mountaincarc": EnvWrapper(env=MountainCarContinuous(num_envs=1, viz=True, device=torch.device("cpu"))),
    "pendulum": EnvWrapper(env=Pendulum(num_envs=1, viz=True, device=torch.device("cpu"))),
    "lunarlander": EnvWrapper(
        env=LunarLander(num_envs=1, continuous=False, viz=True, device=torch.device("cpu"))
    ),
    "lunarlanderc": EnvWrapper(
        env=LunarLander(num_envs=1, continuous=True, viz=True, device=torch.device("cpu"))
    ),
}


def main(args):
    assert args.env[0] in available_env_dict.keys(), f"Unknow Environment {args.env}"
    env_wrapper: EnvWrapper = available_env_dict[args.env[0]]
    env_wrapper = env_wrapper.awake()
    loaded_model = torch.load(trained_model_path_dict[args.env[0]][args.alg[0]])
    loaded_model.eval()
    print(trained_model_path_dict[args.env[0]][args.alg[0]])
    total_reward = 0
    while True:
        o, _ = env_wrapper.reset()
        d = False
        while not d:
            a = loaded_model.act(
                torch.as_tensor(o, dtype=torch.float32)
            )  # in torch.Tensor,no gradient computed
            next_o, r, d, cache = env_wrapper.step(a)
            total_reward += r
            if d:
                print("total reward: ", total_reward.item())
                total_reward = 0
            o = next_o


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--render", action="store_true")
    parser.add_argument("--env", required=True, nargs=1, choices=available_env_dict.keys())
    parser.add_argument("--alg", required=True, nargs=1, choices=available_algs)

    args = parser.parse_args()
    main(args)
