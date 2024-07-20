import os
import pathlib
import torch
from datetime import datetime, timezone

from rlvortex.envs.gym_wrapper.gym_envs import (
    CartPole,
    LunarLander,
    MountainCarContinuous,
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

global_seed = 1997031411


trainer_utils.set_global_random_seed(rd_seed=global_seed)
torch.set_printoptions(precision=10)
# hints to tuning hyperparameters:
# 1. use small batch size instead of train all the transitions in the replay buffer at one time
# 2. enable 1) max_grad_norm 2)normalize_act can lead to difference results
# 3. try to find an apporiate learning iteration
# 4. pay attention to the eposide length of the env, num_transitions_per_env should be larger if the eposide is longer


class CartpoleEnvParams:
    comment = "ppo_cartpole"
    env_fn = CartPole
    num_envs = 8
    device = torch.device("cpu")
    env_wrapper = EnvWrapper(
        env=env_fn(num_envs=num_envs, viz=False, seed=global_seed, device=torch.device("cpu"))
    )
    eva_env_wrapper = EnvWrapper(env=env_fn(num_envs=1, viz=True, seed=global_seed))
    eva_eposides = 1
    policy = policy.A2CPolicy(
        actor=modules.CategoricalActor(
            net=quick_build.mlp([*env_wrapper.observation_dim, 32, env_wrapper.action_n], torch.nn.Tanh)
        ),
        critic=modules.BaseCriticModule(
            net=quick_build.mlp([*env_wrapper.observation_dim, 32, 1], torch.nn.Tanh)
        ),
    )
    epochs = 15
    trainer_folder: os.PathLike = pathlib.Path(
        os.path.join(
            os.getcwd(),
            "trainer_cache",
            f"{ datetime.now(timezone.utc).astimezone().strftime('%d-%m-%y#%H:%M:%S')}_{comment}",
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
        algorithm=algs.PPO(
            policy=policy,
            optimizer_fn=torch.optim.Adam,
            init_lr=1e-3,
            lr_range=(1e-4, 1e-3),
            vf_coef=0.5,
            ent_coef=0.01,
            gamma=0.998,
            lam=0.95,
            max_grad_norm=None,
            learning_iterations=16,
            batch_size=256,
            clip_ratio=0.2,
            dual_clip_ratio=None,
            value_loss_clip=False,
            update_break=False,
            desired_kl=None,
        ),
        flow_logger=vlogger.FlowLogger(
            log_types=[vlogger.LogType.Screen, vlogger.LogType.Board],
            log_path=pathlib.Path(os.path.join(trainer_folder, "logs")),
            board_dir=pathlib.Path(os.path.join(trainer_folder, "runs")),
            comment=comment,
        ),
        save_interval=-1,
        save_path=pathlib.Path(os.path.join(trainer_folder, "models")),
        device=device,
    )


class PendulumEnvParams:
    comment = "ppo_pendulum"
    env_fn = Pendulum
    num_envs = 1
    device = torch.device("cpu")
    env_wrapper = EnvWrapper(
        env=env_fn(num_envs=num_envs, viz=False, seed=global_seed, device=torch.device("cpu"))
    )
    eva_env_wrapper = EnvWrapper(env=env_fn(num_envs=1, viz=True, seed=global_seed))
    eva_eposides = 1
    policy = policy.A2CPolicy(
        actor=modules.GaussianActor(
            net=quick_build.mlp(
                [*env_wrapper.observation_dim, 64, *env_wrapper.action_dim],
                torch.nn.ReLU,
                output_activation=torch.nn.Tanh,
            ),
            init_log_stds=-0.5 * torch.ones(env_wrapper.action_dim),
        ),
        critic=modules.BaseCriticModule(
            net=quick_build.mlp([*env_wrapper.observation_dim, 32, 1], torch.nn.ReLU)
        ),
    )
    epochs = 50
    trainer_folder: os.PathLike = pathlib.Path(
        os.path.join(
            os.getcwd(),
            "trainer_cache",
            f"{ datetime.now(timezone.utc).astimezone().strftime('%d-%m-%y#%H:%M:%S')}_{comment}",
        )
    )
    trainer: rltrainer.OnPolicyTrainer = rltrainer.OnPolicyTrainer(  # noqa: F821
        collector=collectors.TransitionCollector(
            env_wrapper=env_wrapper,
            policy=policy,
            replay_buffer=replay_buffer.TransitionReplayBuffer(
                num_envs=num_envs,
                num_transitions_per_env=2048,
                obs_dim=env_wrapper.env.observation_dim,
                act_dim=env_wrapper.env.action_dim,
                device=device,
            ),
        ),
        algorithm=algs.PPO(
            policy=policy,
            optimizer_fn=torch.optim.Adam,
            init_lr=1e-3,
            lr_range=(1e-4, 1e-3),
            normalize_adv=False,
            vf_coef=0.5,
            ent_coef=0.01,
            gamma=0.9,
            lam=0.95,
            max_grad_norm=0.5,
            learning_iterations=32,
            batch_size=64,
            clip_ratio=0.2,
            dual_clip_ratio=None,
            value_loss_clip=False,
            update_break=False,
            desired_kl=1e-4,
        ),
        flow_logger=vlogger.FlowLogger(
            log_types=[vlogger.LogType.Screen, vlogger.LogType.Board],
            log_path=pathlib.Path(os.path.join(trainer_folder, "logs")),
            board_dir=pathlib.Path(os.path.join(trainer_folder, "runs")),
            comment="ppo_pendulum",
        ),
        save_interval=-1,
        save_path=pathlib.Path(os.path.join(trainer_folder, "models")),
        device=device,
    )


class MountainCarContinuousEnvParams:
    comment = "ppo_mountiancarc"
    env_fn = MountainCarContinuous
    num_envs = 1
    device = torch.device("cpu")
    env_wrapper = EnvWrapper(
        env=env_fn(num_envs=num_envs, viz=False, seed=global_seed, device=torch.device("cpu"))
    )
    eva_env_wrapper = EnvWrapper(env=env_fn(num_envs=1, viz=True, seed=global_seed))
    eva_eposides = 1
    policy = policy.A2CPolicy(
        actor=modules.GaussianActor(
            net=quick_build.mlp(
                [*env_wrapper.observation_dim, 32, *env_wrapper.action_dim],
                torch.nn.Tanh,
                output_activation=torch.nn.Tanh,
            ),
            init_log_stds=-0.5 * torch.ones(env_wrapper.action_dim),
        ),
        critic=modules.BaseCriticModule(
            net=quick_build.mlp([*env_wrapper.observation_dim, 32, 1], torch.nn.Tanh)
        ),
    )
    epochs = 30
    trainer_folder: os.PathLike = pathlib.Path(
        os.path.join(
            os.getcwd(),
            "trainer_cache",
            f"{ datetime.now(timezone.utc).astimezone().strftime('%d-%m-%y#%H:%M:%S')}_{comment}",
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
        algorithm=algs.PPO(
            policy=policy,
            optimizer_fn=torch.optim.Adam,
            init_lr=5e-3,
            lr_range=(1e-4, 1e-3),
            normalize_adv=False,
            vf_coef=2.0,
            ent_coef=0.01,
            gamma=0.998,
            lam=0.95,
            max_grad_norm=None,
            learning_iterations=128,
            batch_size=1024,
            clip_ratio=0.2,
            dual_clip_ratio=None,
            value_loss_clip=False,
            update_break=False,
            desired_kl=None,
        ),
        flow_logger=vlogger.FlowLogger(
            log_types=[vlogger.LogType.Screen, vlogger.LogType.Board],
            log_path=pathlib.Path(os.path.join(trainer_folder, "logs")),
            board_dir=pathlib.Path(os.path.join(trainer_folder, "runs")),
            comment=comment,
        ),
        save_interval=-1,
        save_path=pathlib.Path(os.path.join(trainer_folder, "models")),
        device=device,
    )


class LunarLanderContinuousEnvParams:
    comment = "ppo_lunarlanderc"
    env_fn = LunarLander
    num_envs = 1
    device = torch.device("cpu")
    env_wrapper = EnvWrapper(
        env=env_fn(
            num_envs=num_envs, continuous=True, viz=False, seed=global_seed, device=torch.device("cpu")
        )
    )
    eva_env_wrapper = EnvWrapper(env=env_fn(num_envs=1, continuous=True, viz=True, seed=global_seed))
    eva_eposides = 1
    policy = policy.A2CPolicy(
        actor=modules.GaussianActor(
            net=quick_build.mlp(
                [*env_wrapper.observation_dim, 32, *env_wrapper.action_dim],
                torch.nn.Tanh,
            ),
            init_log_stds=-0.5 * torch.ones(env_wrapper.action_dim),
        ),
        critic=modules.BaseCriticModule(
            net=quick_build.mlp([*env_wrapper.observation_dim, 32, 1], torch.nn.Tanh)
        ),
    )
    epochs = 150
    trainer_folder: os.PathLike = pathlib.Path(
        os.path.join(
            os.getcwd(),
            "trainer_cache",
            f"{ datetime.now(timezone.utc).astimezone().strftime('%d-%m-%y#%H:%M:%S')}_{comment}",
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
        algorithm=algs.PPO(
            policy=policy,
            optimizer_fn=torch.optim.Adam,
            init_lr=1e-3,
            lr_range=(1e-4, 1e-3),
            normalize_adv=True,
            vf_coef=1.0,
            ent_coef=0.01,
            gamma=0.998,
            lam=0.95,
            max_grad_norm=0.5,
            learning_iterations=128,
            batch_size=1024,
            clip_ratio=0.2,
            dual_clip_ratio=None,
            value_loss_clip=False,
            desired_kl=None,
            update_break=False,
        ),
        flow_logger=vlogger.FlowLogger(
            log_types=[vlogger.LogType.Screen, vlogger.LogType.Board],
            log_path=pathlib.Path(os.path.join(trainer_folder, "logs")),
            board_dir=pathlib.Path(os.path.join(trainer_folder, "runs")),
            comment=comment,
        ),
        save_interval=50,
        save_path=pathlib.Path(os.path.join(trainer_folder, "models")),
        device=device,
    )


class LunarLanderEnvParams:
    comment = "ppo_lunarlander"
    env_fn = LunarLander
    num_envs = 1
    device = torch.device("cpu")
    env_wrapper = EnvWrapper(
        env=env_fn(
            num_envs=num_envs, continuous=False, viz=False, seed=global_seed, device=torch.device("cpu")
        )
    )
    eva_env_wrapper = EnvWrapper(env=env_fn(num_envs=1, continuous=False, viz=True, seed=global_seed))
    eva_eposides = 1
    policy = policy.A2CPolicy(
        actor=modules.CategoricalActor(
            net=quick_build.mlp([*env_wrapper.observation_dim, 32, env_wrapper.action_n], torch.nn.Tanh)
        ),
        critic=modules.BaseCriticModule(
            net=quick_build.mlp([*env_wrapper.observation_dim, 32, 1], torch.nn.Tanh)
        ),
    )
    epochs = 250
    trainer_folder: os.PathLike = pathlib.Path(
        os.path.join(
            os.getcwd(),
            "trainer_cache",
            f"{ datetime.now(timezone.utc).astimezone().strftime('%d-%m-%y#%H:%M:%S')}_{comment}",
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
        algorithm=algs.PPO(
            policy=policy,
            optimizer_fn=torch.optim.Adam,
            init_lr=1e-3,
            lr_range=(1e-4, 1e-3),
            normalize_adv=True,
            vf_coef=1.0,
            ent_coef=0.01,
            gamma=0.998,
            lam=0.95,
            max_grad_norm=0.5,
            learning_iterations=128,
            batch_size=1024,
            clip_ratio=0.2,
            dual_clip_ratio=None,
            value_loss_clip=False,
            update_break=True,
            desired_kl=1e-4,
        ),
        flow_logger=vlogger.FlowLogger(
            log_types=[vlogger.LogType.Screen, vlogger.LogType.Board],
            log_path=pathlib.Path(os.path.join(trainer_folder, "logs")),
            board_dir=pathlib.Path(os.path.join(trainer_folder, "runs")),
            comment=comment,
        ),
        save_interval=50,
        save_path=pathlib.Path(os.path.join(trainer_folder, "models")),
        device=device,
    )
