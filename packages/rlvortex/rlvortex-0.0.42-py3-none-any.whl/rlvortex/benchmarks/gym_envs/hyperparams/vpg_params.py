import os
import pathlib
import torch
from rlvortex.policy import PGPolicy
from rlvortex.collectors import EposideCollector
from rlvortex.replay_buffer import EposideReplayBuffer
from rlvortex.algs import VPG
from rlvortex.policy.ppo_policy import CategoricalActor, GaussianActor
from rlvortex.policy.quick_build import mlp
from rlvortex.trainer import OnPolicyTrainer
from rlvortex.envs import EnvWrapper
from rlvortex.envs.gym_wrapper.gym_envs import (
    CartPole,
    LunarLander,
    MountainCarContinuous,
    Pendulum,
)
from rlvortex.utils import trainer_utils, vlogger
from datetime import datetime, timezone

global_seed = 19970314


trainer_utils.set_global_random_seed(rd_seed=global_seed)
torch.set_printoptions(precision=10)


class CartpoleEnvParams:
    env_fn = CartPole
    num_envs = 8
    device = torch.device("cpu")
    env_wrapper = EnvWrapper(
        env=env_fn(num_envs=num_envs, viz=False, seed=global_seed, device=torch.device("cpu"))
    )
    eva_env_wrapper = EnvWrapper(env=env_fn(num_envs=1, viz=True, seed=global_seed))
    eva_epoch = 1
    policy = PGPolicy(
        model=CategoricalActor(
            net=mlp([*env_wrapper.observation_dim, 32, env_wrapper.action_n], torch.nn.Tanh)
        ),
    )
    epochs = 200
    trainer_folder: os.PathLike = pathlib.Path(
        os.path.join(
            os.getcwd(),
            "trainer_cache",
            f"{ datetime.now(timezone.utc).astimezone().strftime('%H:%M:%S#%d-%m-%y')}",
        )
    )
    trainer: OnPolicyTrainer = OnPolicyTrainer(  # noqa: F821
        collector=EposideCollector(
            env_wrapper=env_wrapper,
            policy=policy,
            replay_buffer=EposideReplayBuffer(
                num_envs=num_envs,
                num_eposides=16,
                obs_dim=env_wrapper.env.observation_dim,
                act_dim=env_wrapper.env.action_dim,
                device=device,
            ),
        ),
        algorithm=VPG(policy=policy, optimzer_fn=torch.optim.Adam, init_lr=1e-2, gamma=1.0),
        flow_logger=vlogger.FlowLogger(
            log_types=[vlogger.LogType.Screen, vlogger.LogType.Board],
            log_path=pathlib.Path(os.path.join(trainer_folder, "logs")),
            board_dir=pathlib.Path(os.path.join(trainer_folder, "runs")),
            comment="pg_cartpole",
        ),
        save_interval=-1,
        save_path=pathlib.Path(os.path.join(trainer_folder, "models")),
        device=device,
    )


class PendulumEnvParams:
    # failed to solve
    env_fn = Pendulum
    num_envs = 1
    device = torch.device("cpu")
    env_wrapper = EnvWrapper(
        env=env_fn(num_envs=num_envs, viz=False, seed=global_seed, device=torch.device("cpu"))
    )
    eva_env_wrapper = EnvWrapper(env=env_fn(num_envs=1, viz=True, seed=global_seed))
    eva_epoch = 1
    policy = PGPolicy(
        model=GaussianActor(
            net=mlp(
                [*env_wrapper.observation_dim, 32, *env_wrapper.action_dim],
                torch.nn.Tanh,
                # output_activation=torch.nn.Tanh,
            ),
            init_log_stds=-0.5 * torch.ones(env_wrapper.action_dim),
        ),
    )
    epochs = 2000
    trainer_folder: os.PathLike = pathlib.Path(
        os.path.join(
            os.getcwd(),
            "trainer_cache",
            f"{ datetime.now(timezone.utc).astimezone().strftime('%H:%M:%S#%d-%m-%y')}",
        )
    )
    trainer: OnPolicyTrainer = OnPolicyTrainer(  # noqa: F821
        collector=EposideCollector(
            env_wrapper=env_wrapper,
            policy=policy,
            replay_buffer=EposideReplayBuffer(
                num_envs=num_envs,
                num_eposides=100,
                obs_dim=env_wrapper.env.observation_dim,
                act_dim=env_wrapper.env.action_dim,
                device=device,
            ),
        ),
        algorithm=VPG(policy=policy, optimzer_fn=torch.optim.Adam, init_lr=1e-2, gamma=1.0),
        flow_logger=vlogger.FlowLogger(
            log_types=[vlogger.LogType.Screen, vlogger.LogType.Board],
            log_path=pathlib.Path(os.path.join(trainer_folder, "logs")),
            board_dir=pathlib.Path(os.path.join(trainer_folder, "runs")),
            comment="vpg_pendulum",
        ),
        save_interval=-1,
        save_path=pathlib.Path(os.path.join(trainer_folder, "models")),
        device=device,
    )


class MountainCarContinuousEnvParams:
    # failed to solve
    env_fn = MountainCarContinuous
    num_envs = 1
    device = torch.device("cpu")
    env_wrapper = EnvWrapper(
        env=env_fn(num_envs=num_envs, viz=False, seed=global_seed, device=torch.device("cpu"))
    )
    eva_env_wrapper = EnvWrapper(env=env_fn(num_envs=1, viz=True, seed=global_seed))
    eva_epoch = 1
    policy = PGPolicy(
        model=GaussianActor(
            net=mlp(
                [*env_wrapper.observation_dim, 32, *env_wrapper.action_dim],
                torch.nn.ReLU,
                output_activation=torch.nn.Tanh,
            ),
            init_log_stds=0.5 * torch.ones(env_wrapper.action_dim),
        ),
    )
    epochs = 2000
    trainer_folder: os.PathLike = pathlib.Path(
        os.path.join(
            os.getcwd(),
            "trainer_cache",
            f"{ datetime.now(timezone.utc).astimezone().strftime('%H:%M:%S#%d-%m-%y')}",
        )
    )
    trainer: OnPolicyTrainer = OnPolicyTrainer(  # noqa: F821
        collector=EposideCollector(
            env_wrapper=env_wrapper,
            policy=policy,
            replay_buffer=EposideReplayBuffer(
                num_envs=num_envs,
                num_eposides=8,
                obs_dim=env_wrapper.env.observation_dim,
                act_dim=env_wrapper.env.action_dim,
                device=device,
            ),
        ),
        algorithm=VPG(policy=policy, optimzer_fn=torch.optim.Adam, init_lr=1e-2, gamma=0.99),
        flow_logger=vlogger.FlowLogger(
            log_types=[vlogger.LogType.Screen, vlogger.LogType.Board],
            log_path=pathlib.Path(os.path.join(trainer_folder, "logs")),
            board_dir=pathlib.Path(os.path.join(trainer_folder, "runs")),
            comment="vpg_mountaincarc",
        ),
        save_interval=-1,
        save_path=pathlib.Path(os.path.join(trainer_folder, "models")),
        device=device,
    )


class LunarLanderEnvParams:
    comment = "vpg_lunarlander"
    env_fn = LunarLander
    num_envs = 1
    device = torch.device("cpu")
    env_wrapper = EnvWrapper(
        env=env_fn(num_envs=num_envs, viz=False, seed=global_seed, device=torch.device("cpu"))
    )
    eva_env_wrapper = EnvWrapper(env=env_fn(num_envs=1, viz=True, seed=global_seed))
    eva_steps = 500
    policy = PGPolicy(
        model=CategoricalActor(
            net=mlp([*env_wrapper.observation_dim, 32, env_wrapper.action_n], torch.nn.Tanh)
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
    trainer: OnPolicyTrainer = OnPolicyTrainer(  # noqa: F821
        collector=EposideCollector(
            env_wrapper=env_wrapper,
            policy=policy,
            replay_buffer=EposideReplayBuffer(
                num_envs=num_envs,
                num_eposides=100,
                obs_dim=env_wrapper.env.observation_dim,
                act_dim=env_wrapper.env.action_dim,
                device=device,
            ),
        ),
        algorithm=VPG(policy=policy, optimzer_fn=torch.optim.Adam, init_lr=1e-2, gamma=1.0),
        flow_logger=vlogger.FlowLogger(
            log_types=[vlogger.LogType.Screen, vlogger.LogType.Board],
            log_path=pathlib.Path(os.path.join(trainer_folder, "logs")),
            board_dir=pathlib.Path(os.path.join(trainer_folder, "runs")),
            comment="vpg_lunarlander",
        ),
        save_interval=-1,
        save_path=pathlib.Path(os.path.join(trainer_folder, "models")),
        device=device,
    )


class LunarLanderContinuousEnvParams:
    env_fn = LunarLander
    num_envs = 1
    device = torch.device("cpu")
    env_wrapper = EnvWrapper(
        env=env_fn(
            num_envs=num_envs,
            continuous=True,
            viz=False,
            seed=global_seed,
            device=torch.device("cpu"),
        )
    )
    eva_env_wrapper = EnvWrapper(env=env_fn(num_envs=1, continuous=True, viz=True, seed=global_seed))
    eva_steps = 500
    policy = PGPolicy(
        model=GaussianActor(
            net=mlp(
                [*env_wrapper.observation_dim, 32, *env_wrapper.action_dim],
                torch.nn.Tanh,
            ),
            init_log_stds=-0.9 * torch.ones(*env_wrapper.action_dim),
        )
    )
    epochs = 200
    trainer_folder: os.PathLike = pathlib.Path(
        os.path.join(
            os.getcwd(),
            "trainer_cache",
            f"{ datetime.now(timezone.utc).astimezone().strftime('%H:%M:%S#%d-%m-%y')}",
        )
    )
    trainer: OnPolicyTrainer = OnPolicyTrainer(  # noqa: F821
        collector=EposideCollector(
            env_wrapper=env_wrapper,
            policy=policy,
            replay_buffer=EposideReplayBuffer(
                num_envs=num_envs,
                num_eposides=128,
                obs_dim=env_wrapper.env.observation_dim,
                act_dim=env_wrapper.env.action_dim,
                device=device,
            ),
        ),
        algorithm=VPG(policy=policy, optimzer_fn=torch.optim.Adam, init_lr=1e-2, gamma=1.0),
        flow_logger=vlogger.FlowLogger(
            log_types=[vlogger.LogType.Screen, vlogger.LogType.Board],
            log_path=pathlib.Path(os.path.join(trainer_folder, "logs")),
            board_dir=pathlib.Path(os.path.join(trainer_folder, "runs")),
            comment="vpg_lunarlander",
        ),
        save_interval=-1,
        save_path=pathlib.Path(os.path.join(trainer_folder, "models")),
        device=device,
    )
