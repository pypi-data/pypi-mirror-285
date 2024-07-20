import argparse
from typing import Dict, Callable, List
from rlvortex.benchmarks.gym_envs.hyperparams import vpg_params
from rlvortex.benchmarks.gym_envs.hyperparams import a2c_params, ppo_params
from rlvortex.trainer import OnPolicyTrainer

task_dict: Dict[str, Dict[str, Callable]] = {
    "cartpole": {
        "vpg": vpg_params.CartpoleEnvParams,
        "a2c": a2c_params.CartpoleEnvParams,
        "ppo": ppo_params.CartpoleEnvParams,
    },
    "pendulum": {
        "vpg": vpg_params.PendulumEnvParams,
        "a2c": a2c_params.PendulumEnvParams,
        "ppo": ppo_params.PendulumEnvParams,
    },
    "mountaincarc": {
        "ppo": ppo_params.MountainCarContinuousEnvParams,
    },
    "lunarlanderc": {
        "ppo": ppo_params.LunarLanderContinuousEnvParams,
    },
    "lunarlander": {
        "ppo": ppo_params.LunarLanderEnvParams,
    },
}

available_algs: List[str] = ["vpg", "a2c", "ppo"]
available_envs: List[str] = ["cartpole", "pendulum", "mountaincarc", "lunarlanderc", "lunarlander"]

solved_scores_dict: Dict[str, float] = {
    "cartpole": 500,
    "pendulum": -150,
    "mountaincarc": 90,
    "lunarlanderc": 250,
    "lunarlander": 250,
}


def main(env_name: str, alg_name: str):
    assert env_name in available_envs, f"Unknow Environment {env_name}"
    assert alg_name in available_algs, f"Unknow Algorithm {alg_name}"

    target_env_params = task_dict[env_name][alg_name]
    train_batch = 3
    trainer: OnPolicyTrainer = target_env_params.trainer
    sub_epochs = int(target_env_params.epochs // train_batch)
    ep_rtn = 0
    for _ in range(train_batch):
        trainer.train(sub_epochs)
        if target_env_params.eva_eposides > 0:
            ep_rtn = trainer.evaluate(target_env_params.eva_eposides, target_env_params.eva_env_wrapper)
            print(f"{env_name} evaluated with reward {ep_rtn}/{solved_scores_dict[env_name]}")

    print(f"the final evaluation get {ep_rtn:.2f} with {solved_scores_dict[env_name]} as solved reward")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", required=True, nargs=1, choices=available_envs)
    parser.add_argument("--alg", required=True, nargs=1, choices=available_algs)
    args = parser.parse_args()
    main(args.env[0], args.alg[0])
