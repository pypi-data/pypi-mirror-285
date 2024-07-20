from typing import Any, Dict, List, Optional, Union, Tuple
import torch
import numpy as np
import gymnasium as gym
from gymnasium.spaces import Box, Discrete
from rlvortex.envs.base_env import BaseEnvTrait
from rlvortex.utils.trainer_utils import unscale_actions, scale_actions


class ClusterGymEnv(BaseEnvTrait):
    def __init__(
        self,
        *,
        num_envs: int,
        normalize_act: bool,
        viz: bool,
        seed: int,
        device: torch.device = torch.device("cpu"),
    ) -> None:
        super().__init__(num_envs=num_envs)
        self.gym_envs: List[Optional[gym.Env]] = [None for _ in range(self.num_envs)]
        self._normalize_act: bool = normalize_act
        self._renderable = viz
        self._seed: Optional[int] = seed
        self._info_steps: List[float] = [0.0 for _ in range(num_envs)]
        self._info_returns: List[float] = [0.0 for _ in range(num_envs)]
        self._reset_buffer: List[bool] = [False for _ in range(num_envs)]
        self.device: torch.device = device

    @property
    def params(self) -> Dict[str, Any]:
        params_dict: Dict[str, Any] = super().params
        params_dict.update(
            {
                "normalize_act": self._normalize_act,
                "viz": self._renderable,
                "seed": self._seed,
                "device": self.device.type,
            }
        )
        return params_dict

    @property
    def seed(self):
        return self._seed

    @property
    def renderable(self):
        return self._renderable

    @property
    def action_dim(self) -> Tuple[int, ...]:
        assert self.gym_envs[0] is not None, "self.gym_envs must not be None"
        if isinstance(self.gym_envs[0].action_space, Discrete):
            return ()
        assert self.gym_envs[0].action_space.shape is not None
        return self.gym_envs[0].action_space.shape

    @property
    def action_n(self) -> np.int64:
        assert self.gym_envs[0] is not None, "self.gym_envs must not be None"
        if isinstance(self.gym_envs[0].action_space, Discrete):
            return self.gym_envs[0].action_space.n
        return np.int64(0)

    @property
    def observation_dim(self) -> Optional[Tuple[int, ...]]:
        assert self.gym_envs[0] is not None, "self.gym must be a gym env, not None"
        return self.gym_envs[0].observation_space.shape

    def awake(self) -> None:
        # only box action space can be normalized
        for env_idx in range(self.num_envs):
            target_env: Optional[gym.Env] = self.gym_envs[env_idx]
            assert target_env is not None, "self.gym must be a gym env, not None"
            if self._normalize_act:
                assert isinstance(
                    target_env.action_space, Box
                ), f"only box action space can be normalized, get type {type(target_env.action_space)}"  # noqa: E501
            assert target_env is not None, "self.gym must be a gym env, not None"

    def reset(self, reset_indices: Optional[List[int]] = None) -> Tuple[torch.Tensor, Dict[str, Any]]:
        if reset_indices is None:
            reset_indices = torch.arange(self.num_envs, dtype=torch.int).tolist()
        observations = []
        for env_idx in reset_indices:
            target_env: Optional[gym.Env] = self.gym_envs[env_idx]
            assert target_env is not None, "self.gym must be a gym env, not None"
            self._info_steps[env_idx] = 0
            self._info_returns[env_idx] = 0.0
            if self._seed is None:
                observation, _ = target_env.reset()
            else:
                observation, _ = target_env.reset(seed=self._seed + env_idx)
            observations.append(observation)
        return torch.tensor(np.array(observations), device=self.device), {}

    def step(self, actions: Union[np.ndarray, torch.Tensor]):
        assert actions.shape == (
            self.num_envs,
            *self.action_dim,
        ), f"actions.shape[0] must be {self.num_envs} but got {actions.shape[0]}"
        observations = []
        rewards = []
        dones = []
        infos = {}
        for env_idx in range(self.num_envs):
            target_env = self.gym_envs[env_idx]
            assert target_env is not None, f"self.gym_envs[{env_idx}] must be a gym env, not None"
            self._info_steps[env_idx] += 1
            action = actions[env_idx]
            if (
                self._normalize_act
                and isinstance(target_env.action_space, Box)
                and (isinstance(actions, np.ndarray) or isinstance(actions, torch.Tensor))
            ):
                action = scale_actions(
                    actions[env_idx],
                    target_env.action_space.low,
                    target_env.action_space.high,
                )
            next_observation, reward, terminated, truncated, info = target_env.step(action.cpu().numpy())
            done = terminated or truncated
            self._info_returns[env_idx] += float(reward)
            if done:
                next_observation, _ = target_env.reset()
            observations.append(next_observation)
            rewards.append(reward)
            dones.append(done)
        infos: Dict[str, List[Optional[torch.Tensor]]] = {
            "returns": [
                torch.tensor(self._info_returns[env_idx], device=self.device) if dones[env_idx] else None
                for env_idx in range(self.num_envs)
            ],
            "ep_lens": [
                torch.tensor(self._info_steps[env_idx], device=self.device) if dones[env_idx] else None
                for env_idx in range(self.num_envs)
            ],
        }
        return (
            torch.tensor(np.array(observations), device=self.device),
            torch.tensor(np.array(rewards), device=self.device),
            torch.tensor(np.array(dones), device=self.device),
            infos,
        )

    def sample_action(self):
        actions = []
        for env_idx in range(self.num_envs):
            target_env = self.gym_envs[env_idx]
            assert target_env is not None, f"self.gym_envs[{env_idx}] must be a gym env, not None"
            if self._normalize_act and isinstance(target_env.action_space, Box):
                actions.append(
                    unscale_actions(
                        target_env.action_space.sample(),
                        target_env.action_space.low,
                        target_env.action_space.high,
                    )
                )
            else:
                actions.append(target_env.action_space.sample())
        return torch.tensor(actions, device=self.device).reshape(self.num_envs, *self.action_dim)

    def render(self):
        assert self._renderable, "environment rendering is not enabled"
        for env_idx in range(self.num_envs):
            target_env = self.gym_envs[env_idx]
            assert target_env is not None, f"self.gym_envs[{env_idx}] must be a gym env, not None"
            target_env.render()

    def destory(self):
        for env_idx in range(self.num_envs):
            target_env = self.gym_envs[env_idx]
            assert target_env is not None, f"self.gym_envs[{env_idx}] must be a gym env, not None"
            return target_env.close()


class CartPole(ClusterGymEnv):
    def __init__(
        self,
        *,
        num_envs: int,
        viz: bool,
        seed: int = 19970314,
        device: torch.device = torch.device("cpu"),
    ) -> None:
        super().__init__(num_envs=num_envs, normalize_act=False, viz=viz, seed=seed, device=device)
        if viz:
            self.gym_envs: List[gym.Env] = [
                gym.make("CartPole-v1", render_mode="human") for _ in range(self.num_envs)
            ]
        else:
            self.gym_envs: List[gym.Env] = [gym.make("CartPole-v1") for _ in range(self.num_envs)]

    @property
    def params(self) -> Dict[str, Any]:
        params_dict: Dict[str, Any] = super().params
        params_dict["name"] = "CartPole"
        return params_dict


class LunarLander(ClusterGymEnv):
    def __init__(
        self,
        *,
        num_envs: int,
        continuous: bool = False,
        viz: bool = False,
        seed: int = 19970314,
        device=torch.device("cpu"),
    ) -> None:
        super().__init__(num_envs=num_envs, normalize_act=False, viz=viz, seed=seed, device=device)
        self.continuous = continuous
        if viz:
            self.gym_envs: List[gym.Env] = [
                gym.make("LunarLander-v2", continuous=continuous, render_mode="human")
                for _ in range(self.num_envs)
            ]
        else:
            self.gym_envs: List[gym.Env] = [
                gym.make("LunarLander-v2", continuous=continuous) for _ in range(self.num_envs)
            ]

    @property
    def params(self) -> Dict[str, Any]:
        params_dict: Dict[str, Any] = super().params
        params_dict.update({"continuous": self.continuous, "name": "LunarLander"})
        return params_dict


class Pendulum(ClusterGymEnv):
    def __init__(
        self,
        num_envs: int,
        viz: bool = False,
        seed: int = 19970314,
        device=torch.device("cpu"),
    ) -> None:
        super().__init__(num_envs=num_envs, normalize_act=True, viz=viz, seed=seed, device=device)
        if viz:
            self.gym_envs: List[gym.Env] = [
                gym.make("Pendulum-v1", render_mode="human") for _ in range(self.num_envs)
            ]
        else:
            self.gym_envs: List[gym.Env] = [gym.make("Pendulum-v1") for _ in range(self.num_envs)]

    @property
    def params(self) -> Dict[str, Any]:
        params_dict: Dict[str, Any] = super().params
        params_dict.update({"name": "LunarLander"})
        return params_dict


class MountainCarContinuous(ClusterGymEnv):
    def __init__(
        self,
        *,
        num_envs: int,
        viz: bool = False,
        seed: int = 19970314,
        device=torch.device("cpu"),
    ) -> None:
        super().__init__(num_envs=num_envs, normalize_act=False, viz=viz, seed=seed, device=device)
        if viz:
            self.gym_envs: List[gym.Env] = [
                gym.make("MountainCarContinuous-v0", render_mode="human") for _ in range(self.num_envs)
            ]
        else:
            self.gym_envs: List[gym.Env] = [
                gym.make("MountainCarContinuous-v0") for _ in range(self.num_envs)
            ]

    @property
    def params(self) -> Dict[str, Any]:
        params_dict: Dict[str, Any] = super().params
        params_dict.update({"name": "MountainCarContinuous"})
        return params_dict
