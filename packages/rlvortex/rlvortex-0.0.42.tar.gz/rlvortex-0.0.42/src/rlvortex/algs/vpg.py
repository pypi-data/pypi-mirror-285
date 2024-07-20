from typing import Callable, Dict, Tuple
import torch
from rlvortex.algs import BaseRLAlgorithm
from rlvortex.policy import PGPolicy
from rlvortex.replay_buffer import EposideReplayBuffer
from rlvortex.collectors import EposideCollector


class VPG(BaseRLAlgorithm):
    def __init__(
        self,
        *,
        policy: PGPolicy,
        optimzer_fn: Callable,
        init_lr: float,
        gamma: float,
    ) -> None:
        assert isinstance(policy, PGPolicy), "policy must be an instance of PGPolicy"
        assert (
            isinstance(gamma, float) and 0.0 <= gamma <= 1.0
        ), "gamma must be a float number between 0.0 and 1.0, "
        super().__init__(policy)
        self.policy: PGPolicy = policy
        self._init_lr: float = init_lr
        self._optimizer: torch.optim.Optimizer = optimzer_fn(policy.model.parameters(), lr=init_lr)
        self._gamma: float = gamma

    @property
    def params(self) -> Dict:
        return {
            "name": self.__class__.__name__,
            "init_lr": self._init_lr,
            "gamma": self._gamma,
        }

    def __compute_returns(self, collector: EposideCollector) -> Dict[str, torch.Tensor]:
        replay_buffer: EposideReplayBuffer = collector.replay_buffer
        assert replay_buffer.is_full, "replayer buffer must be fullfiled before processing"
        next_values = torch.tensor(0, device=replay_buffer.device)
        replay_buffer.data_dict["returns"] = torch.zeros(
            replay_buffer.num_transistions, device=replay_buffer.device
        )
        for step in reversed(range(replay_buffer.num_transistions)):
            next_values = (
                replay_buffer.data_dict["rewards"][step]
                + self._gamma * (1 - replay_buffer.data_dict["dones"][step]) * next_values
            )
            replay_buffer.data_dict["returns"][step] = next_values
        return {}

    def update(self, collector: EposideCollector) -> Dict[str, torch.Tensor]:
        data_dict: Dict[str, torch.Tensor] = collector.replay_buffer.data_dict
        self.__compute_returns(collector)
        self._optimizer.zero_grad()
        observations = data_dict["observations"]
        actions = data_dict["actions"]
        returns = data_dict["returns"]
        loss, action_prob = self._compute_loss(observations, actions, returns)
        loss.backward()
        self._optimizer.step()
        collector.clear()
        return {"loss/pi_loss": loss, "policy/action_prob": action_prob}

    def _compute_loss(
        self, observations: torch.Tensor, actions: torch.Tensor, returns: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        logp_a = self.policy(observations, actions)
        loss = -(logp_a * returns).mean()
        return loss, logp_a.detach().exp().mean()
