from abc import ABC, abstractmethod
from typing import Dict
import torch
from rlvortex.policy import BasePolicy
from rlvortex.collectors import BaseCollector


class BaseRLAlgorithm(ABC):
    def __init__(
        self,
        policy: BasePolicy,
    ) -> None:
        assert isinstance(policy, BasePolicy), "policy must be an instance of BasePolicy"
        self.policy: BasePolicy = policy

    @abstractmethod
    def update(self, collector: BaseCollector) -> Dict[str, torch.Tensor]:
        """
        return dict of data that will be stored in the flow logger for logging
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def params(self):
        raise NotImplementedError
