from typing import Any, Tuple, Dict

import torch

from rlvortex.replay_buffer import BaseReplayBuffer


class TransitionReplayBuffer(BaseReplayBuffer):
    def __init__(
        self,
        num_envs: int,
        num_transitions_per_env: int,
        obs_dim: Tuple[int, ...],
        act_dim: Tuple[int, ...],
        device: torch.device,
    ) -> None:
        assert isinstance(num_envs, int)
        assert (
            isinstance(num_transitions_per_env, int) and num_transitions_per_env > 0
        ), "batch_steps_per_env must be a positive integer"
        assert isinstance(device, torch.device), "device must be an instance of Device"
        super().__init__(num_envs, device)
        self.obs_dim: Tuple[int, ...] = obs_dim
        self.act_dim: Tuple[int, ...] = act_dim
        self.num_transitions_per_env: int = num_transitions_per_env
        self.data_dict = {
            "observations": torch.zeros(
                self.num_transitions_per_env, self.num_envs, *obs_dim, device=device
            ),
            "actions": torch.zeros(self.num_transitions_per_env, self.num_envs, *act_dim, device=device),
            "rewards": torch.zeros(self.num_transitions_per_env, self.num_envs, device=device),
            "dones": torch.zeros(self.num_transitions_per_env, self.num_envs, device=device),
            "returns": torch.zeros(self.num_transitions_per_env, self.num_envs, device=device),
        }
        self._steps = 0

    @property
    def params(self) -> Dict[str, Any]:
        params_dict: Dict = super().params
        params_dict.update(
            {
                "num_transitions_per_env": self.num_transitions_per_env,
                "obs_dim": self.obs_dim,
                "act_dim": self.act_dim,
            }
        )
        return params_dict

    @property
    def is_full(self) -> bool:
        return self._steps >= self.num_transitions_per_env

    @property
    def num_transitions_total(self) -> int:
        return self.num_envs * self.num_transitions_per_env

    def clear(self) -> None:
        self._steps = 0

    def append(
        self,
        observations: torch.Tensor,
        actions: torch.Tensor,
        rewards: torch.Tensor,
        dones: torch.Tensor,
        extra_info: Dict[str, torch.Tensor],
    ):
        assert not self.is_full, (
            f"replayer buffer is full, step must be less than {self.num_transitions_per_env}, "  # noqa: E501
            f"but got {self._steps}"
        )
        assert observations.shape == (self.num_envs, *self.obs_dim), (
            f"observations.shape must be {self.num_envs, *self.obs_dim}" f"but got {observations.shape}"
        )
        assert actions.shape == (self.num_envs, *self.act_dim), (
            f"actions.shape must be {self.num_envs, *self.act_dim}" f"but got {actions.shape}"
        )
        assert rewards.shape == (self.num_envs,), (
            f"rewards.shape must be {(self.num_envs,1)}" f"but got {rewards.shape}"
        )
        assert dones.shape == (self.num_envs,), (
            f"dones.shape must be {(self.num_envs,1)}" f"but got {dones.shape}"
        )
        self.data_dict["observations"][self._steps] = observations
        self.data_dict["actions"][self._steps] = actions
        self.data_dict["rewards"][self._steps] = rewards
        self.data_dict["dones"][self._steps] = dones
        for key, value in extra_info.items():
            assert key not in ["observations", "actions", "rewards", "dones"]
            if key not in self.data_dict:
                self.data_dict[key] = torch.zeros(
                    self.num_transitions_per_env,
                    *value.shape,
                    device=self.device,
                )
            self.data_dict[key][self._steps] = value
        self._steps += 1
