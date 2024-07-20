from typing import Any, Dict, List, Optional, Tuple
import torch
from rlvortex.collectors import BaseCollector
from rlvortex.replay_buffer import (
    TransitionReplayBuffer,
    EposideReplayBuffer,
)
from rlvortex.policy import BasePolicy
from rlvortex.envs import EnvWrapper


class TransitionCollector(BaseCollector):
    def __init__(
        self,
        env_wrapper: EnvWrapper,
        policy: BasePolicy,
        replay_buffer: TransitionReplayBuffer,
    ) -> None:
        super().__init__(env_wrapper, replay_buffer, policy)
        self.replay_buffer: TransitionReplayBuffer
        self.env_wrapper.awake()
        self._observations, _ = self.env_wrapper.reset()

    @property
    def params(self) -> Dict[str, Any]:
        return super().params

    def collect(self) -> None:
        assert self._observations is not None, "observations must not be None"
        for _ in range(self.replay_buffer.num_transitions_per_env):
            if self.policy is None:
                actions, policy_info = self.env_wrapper.sample_action(), {}
            else:
                actions, policy_info = self.policy.step(self._observations)
            next_observations, rewards, dones, envs_data = self.env_wrapper.step(actions)
            policy_info["next_observations"] = next_observations
            self._on_step(envs_data)
            self.replay_buffer.append(
                self._observations,
                actions,
                rewards,
                dones,
                policy_info,
            )
            if torch.any(dones):
                done_indices = torch.where(dones)
                reset_indices: List[int] = done_indices[0].cpu().tolist()
                if self.flow_meter is not None:
                    self.flow_meter.store_episode_data(envs_data)
                reset_observations, _ = self.env_wrapper.reset(reset_indices)
                next_observations[done_indices] = reset_observations
            self._observations = next_observations


class EposideRecorder:
    def __init__(
        self,
        *,
        num_envs: int,
        obs_dim: Tuple[int, ...],
        act_dim: Tuple[int, ...],
        device: torch.device,
    ) -> None:
        assert num_envs > 0, "num_envs must be a positive integer"
        assert isinstance(device, torch.device), "device must be an instance of Device"
        self.num_envs: int = num_envs
        self._obs_dim: Tuple[int, ...] = obs_dim
        self._act_dim: Tuple[int, ...] = act_dim
        self.device = device
        self.eposide_data_dict: Dict[str, List[List[torch.Tensor]]] = {
            "observations": [[] for _ in range(self.num_envs)],
            "actions": [[] for _ in range(self.num_envs)],
            "rewards": [[] for _ in range(self.num_envs)],
            "dones": [[] for _ in range(self.num_envs)],
            "returns": [[] for _ in range(self.num_envs)],
        }

    def clear(self, done_indices) -> None:
        for done_idx in done_indices:
            for key in self.eposide_data_dict.keys():
                self.eposide_data_dict[key][done_idx] = []

    def append(
        self,
        observations: torch.Tensor,
        actions: torch.Tensor,
        rewards: torch.Tensor,
        dones: torch.Tensor,
        step_info: Dict[str, torch.Tensor],
    ):
        assert observations.shape == (self.num_envs, *self._obs_dim), (
            f"observations.shape must be {self.num_envs, *self._obs_dim}" f" but got {observations.shape}"
        )
        assert actions.shape == (self.num_envs, *self._act_dim), (
            f"actions.shape must be {self.num_envs, *self._act_dim}" f"but got {actions.shape}"
        )
        assert rewards.shape == (
            self.num_envs,
        ), f"rewards.shape must be {(self.num_envs,)} but got {rewards.shape}"
        assert dones.shape == (
            self.num_envs,
        ), f"dones.shape must be {(self.num_envs,)} but got {dones.shape}"
        for env_id in range(self.num_envs):
            self.eposide_data_dict["observations"][env_id].append(observations[env_id])
            self.eposide_data_dict["actions"][env_id].append(actions[env_id])
            self.eposide_data_dict["rewards"][env_id].append(rewards[env_id])
            self.eposide_data_dict["dones"][env_id].append(dones[env_id])
            for key, value in step_info.items():
                assert key not in ["observations", "actions", "rewards", "dones"], (
                    f"key must not be one of ['observations', 'actions', 'rewards', 'dones'], "
                    f"but got {key}"
                )
                if key not in self.eposide_data_dict:
                    self.eposide_data_dict[key] = [[] for _ in range(self.num_envs)]
                self.eposide_data_dict[key][env_id].append(value[env_id])


class EposideCollector(BaseCollector):
    def __init__(
        self,
        env_wrapper: EnvWrapper,
        replay_buffer: EposideReplayBuffer,
        policy: Optional[BasePolicy] = None,
    ) -> None:
        super().__init__(env_wrapper, replay_buffer, policy)
        self.replay_buffer: EposideReplayBuffer
        self.eposide_recorder: EposideRecorder = EposideRecorder(
            num_envs=replay_buffer.num_envs,
            obs_dim=env_wrapper.observation_dim,
            act_dim=env_wrapper.action_dim,
            device=replay_buffer.device,
        )
        self._observations, _ = self.env_wrapper.reset()

    @property
    def params(self) -> Dict[str, Any]:
        return super().params

    def _record_eposide_transitions(self, done_indices: List[int]) -> None:
        for done_idx in done_indices:
            if self.replay_buffer.is_full:
                break
            self.replay_buffer.append(
                torch.stack(
                    self.eposide_recorder.eposide_data_dict["observations"][done_idx],
                    dim=0,
                ),
                torch.stack(self.eposide_recorder.eposide_data_dict["actions"][done_idx], dim=0),
                torch.stack(self.eposide_recorder.eposide_data_dict["rewards"][done_idx], dim=0),
                torch.stack(self.eposide_recorder.eposide_data_dict["dones"][done_idx], dim=0),
                {
                    key: torch.stack(val[done_idx], dim=0)
                    for key, val in self.eposide_recorder.eposide_data_dict.items()
                    if key not in ["observations", "actions", "rewards", "dones"] and len(val[done_idx]) > 0
                },
            )
        self.eposide_recorder.clear(done_indices)

    def collect(self):
        assert self._observations is not None, "observations must not be None"
        while not self.replay_buffer.is_full:
            if self.policy is None:
                actions, policy_info = self.env_wrapper.sample_action(), {}
            else:
                actions, policy_info = self.policy.step(self._observations)
            next_observations, rewards, dones, envs_data = self.env_wrapper.step(actions)
            self._on_step(envs_data)
            self.eposide_recorder.append(
                self._observations,
                actions,
                rewards,
                dones,
                policy_info,
            )
            if torch.any(dones):
                done_indices = torch.where(dones)
                reset_indices: List[int] = done_indices[0].cpu().tolist()
                if self.flow_meter is not None:
                    self.flow_meter.store_episode_data(envs_data)
                self._record_eposide_transitions(reset_indices)
                reset_observations, _ = self.env_wrapper.reset(reset_indices)
                next_observations[done_indices] = reset_observations
            self._observations = next_observations
