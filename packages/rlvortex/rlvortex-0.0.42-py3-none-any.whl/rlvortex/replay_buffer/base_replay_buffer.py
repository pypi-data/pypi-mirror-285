import abc
from typing import Any, Dict
import torch


class BaseReplayBuffer(abc.ABC):
    def __init__(self, num_envs: int, device: torch.device) -> None:
        assert isinstance(num_envs, int) and num_envs >= 1
        assert isinstance(device, torch.device), "device must be an instance of Device"
        self.num_envs: int = num_envs
        self.data_dict: Dict[str, torch.Tensor] = {}
        self.device: torch.device = device

    @property
    @abc.abstractmethod
    def params(self) -> Dict[str, Any]:
        return {
            "num_envs": self.num_envs,
            "device": self.device.type,
        }

    @property
    @abc.abstractmethod
    def is_full(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def append(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def clear(self) -> None:
        raise NotImplementedError
