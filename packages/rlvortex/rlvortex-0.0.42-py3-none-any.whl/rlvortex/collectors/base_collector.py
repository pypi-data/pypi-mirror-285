import abc
from typing import Any, Dict, Optional

import torch
from rlvortex.envs import EnvWrapper
from rlvortex.policy.base_policy import BasePolicy
from rlvortex.replay_buffer import BaseReplayBuffer
from rlvortex.utils import vlogger


class BaseCollector(abc.ABC):
    """
    A base class for all collectors. A Collector is used to collect samples from the environment and store them in a replay buffer.
    """

    def __init__(
        self,
        env_wrapper: EnvWrapper,
        replay_buffer: BaseReplayBuffer,
        policy: Optional[BasePolicy],
    ) -> None:
        super().__init__()
        self.env_wrapper: EnvWrapper = env_wrapper.awake()
        self.policy: Optional[BasePolicy] = policy
        self.replay_buffer: BaseReplayBuffer = replay_buffer
        self.flow_meter: Optional[vlogger.BaseFlowMeter] = None
        self._observations: Optional[torch.Tensor] = None

    @property
    @abc.abstractmethod
    def params(self) -> Dict[str, Any]:
        return {
            "replayer_buffer": self.replay_buffer.params,
            "env": self.env_wrapper.env.params,
        }

    def borrow_flow_meter(self, flow_meter: vlogger.BaseFlowMeter) -> None:
        self.flow_meter = flow_meter

    def _on_step(self, envs_data: Dict[str, Any]):
        pass

    @abc.abstractmethod
    def collect(self):
        raise NotImplementedError

    def clear(self):
        self.replay_buffer.clear()
