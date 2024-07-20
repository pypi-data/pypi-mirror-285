import os
import pathlib
import torch
from datetime import datetime, timezone

from rlvortex.envs.gym_wrapper.gym_envs import (
    CartPole,
    Pendulum,
)
import rlvortex.algs as algs
import rlvortex.policy as policy
import rlvortex.policy.ppo_policy as modules
import rlvortex.policy.quick_build as quick_build
import rlvortex.trainer as rltrainer
import rlvortex.collectors as collectors
import rlvortex.replay_buffer as replay_buffer
from rlvortex.envs import EnvWrapper
from rlvortex.utils import trainer_utils, vlogger

global_seed = 19970314


trainer_utils.set_global_random_seed(rd_seed=global_seed)
torch.set_printoptions(precision=10)


class CartpoleEnvParams:
    comment = "a2c_cartpole"
    env_fn = CartPole
    num_envs = 8
    device = torch.device("cpu")
    env_wrapper = EnvWrapper(
        env=env_fn(num_envs=num_envs, viz=False, seed=global_seed, device=torch.device("cpu"))
    )
    eva_env_wrapper = EnvWrapper(env=env_fn(num_envs=1, viz=True, seed=global_seed))
    eva_steps = 200
    policy = policy.A2CPolicy(
        actor=modules.CategoricalActor(
            net=quick_build.mlp([*env_wrapper.observation_dim, 32, env_wrapper.action_n], torch.nn.Tanh)
        ),
        critic=modules.BaseCriticModule(
            net=quick_build.mlp([*env_wrapper.observation_dim, 32, 1], torch.nn.Tanh)
        ),
    )
    epochs = 200
    trainer_folder: os.PathLike = pathlib.Path(
        os.path.join(
            os.getcwd(),
            "trainer_cache",
            f"{ datetime.now(timezone.utc).astimezone().strftime('%H:%M:%S#%d-%m-%y')}_{comment}",
        )
    )
    trainer: rltrainer.OnPolicyTrainer = rltrainer.OnPolicyTrainer(  # noqa: F821
        collector=collectors.TransitionCollector(
            env_wrapper=env_wrapper,
            policy=policy,
            replay_buffer=replay_buffer.TransitionReplayBuffer(
                num_envs=num_envs,
                num_transitions_per_env=1024,
                obs_dim=env_wrapper.env.observation_dim,
                act_dim=env_wrapper.env.action_dim,
                device=device,
            ),
        ),
        algorithm=algs.A2C(
            policy=policy,
            optimizer_fn=torch.optim.Adam,
            init_lr=1e-2,
        ),
        flow_logger=vlogger.FlowLogger(
            log_types=[vlogger.LogType.Screen, vlogger.LogType.Board],
            log_path=pathlib.Path(os.path.join(trainer_folder, "logs")),
            board_dir=pathlib.Path(os.path.join(trainer_folder, "runs")),
            comment="a2c_cartpole",
        ),
        save_interval=-1,
        save_path=pathlib.Path(os.path.join(trainer_folder, "models")),
        device=device,
    )


class PendulumEnvParams:
    comment = "a2c_pendulum"
    env_fn = Pendulum
    num_envs = 1
    device = torch.device("cpu")
    env_wrapper = EnvWrapper(
        env=env_fn(num_envs=num_envs, viz=False, seed=global_seed, device=torch.device("cpu"))
    )
    eva_env_wrapper = EnvWrapper(env=env_fn(num_envs=1, viz=True, seed=global_seed))
    eva_steps = 400
    policy = policy.A2CPolicy(
        actor=modules.GaussianActor(
            net=quick_build.mlp([*env_wrapper.observation_dim, 64, *env_wrapper.action_dim], torch.nn.ReLU),
            init_log_stds=0.1 * torch.ones(env_wrapper.action_dim),
        ),
        critic=modules.BaseCriticModule(
            net=quick_build.mlp([*env_wrapper.observation_dim, 32, 1], torch.nn.ReLU)
        ),
    )
    epochs = 20000
    trainer_folder: os.PathLike = pathlib.Path(
        os.path.join(
            os.getcwd(),
            "trainer_cache",
            f"{ datetime.now(timezone.utc).astimezone().strftime('%H:%M:%S#%d-%m-%y')}_{comment}",
        )
    )
    trainer: rltrainer.OnPolicyTrainer = rltrainer.OnPolicyTrainer(  # noqa: F821
        collector=collectors.TransitionCollector(
            env_wrapper=env_wrapper,
            policy=policy,
            replay_buffer=replay_buffer.TransitionReplayBuffer(
                num_envs=num_envs,
                num_transitions_per_env=4096,
                obs_dim=env_wrapper.env.observation_dim,
                act_dim=env_wrapper.env.action_dim,
                device=device,
            ),
        ),
        algorithm=algs.A2C(
            policy=policy,
            optimizer_fn=torch.optim.Adam,
            init_lr=1e-3,
        ),
        flow_logger=vlogger.FlowLogger(
            log_types=[vlogger.LogType.Screen, vlogger.LogType.Board],
            log_path=pathlib.Path(os.path.join(trainer_folder, "logs")),
            board_dir=pathlib.Path(os.path.join(trainer_folder, "runs")),
            comment="a2c_pendulum",
        ),
        save_interval=-1,
        save_path=pathlib.Path(os.path.join(trainer_folder, "models")),
        device=device,
    )
