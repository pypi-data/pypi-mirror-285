from typing import Callable, Dict, Optional
import torch
from rlvortex.algs import BaseRLAlgorithm
from rlvortex.policy import A2CPolicy
from rlvortex.collectors import TransitionCollector
from rlvortex.replay_buffer import TransitionReplayBuffer
import rlvortex.utils.trainer_utils as trainer_utils


class A2C(BaseRLAlgorithm):
    def __init__(
        self,
        *,
        policy: A2CPolicy,
        init_lr: float,
        optimizer_fn: Callable,
        vf_coef: float = 0.5,
        ent_coef: float = 0.01,
        gamma: float = 0.998,
        lam: float = 0.97,
        max_grad_norm: Optional[float] = None,
    ) -> None:
        assert isinstance(policy, A2CPolicy), "policy must be an instance of PGPolicy"
        assert (
            isinstance(gamma, float) and 0.0 <= gamma <= 1.0
        ), "gamma must be a float number between 0.0 and 1.0, "
        super().__init__(policy)
        self._policy: A2CPolicy = policy
        self._init_lr: float = init_lr
        self._optimizer: torch.optim.Optimizer = optimizer_fn(policy.parameters(), lr=init_lr)
        self._vf_coef: float = vf_coef
        self._ent_coef: float = ent_coef
        self._gamma: float = gamma
        self._lam: float = lam
        self._max_grad_norm: Optional[float] = max_grad_norm

    @property
    def params(self):
        return {
            "name": self.__class__.__name__,
            "lr": self._init_lr,
            "vf_coef": self._vf_coef,
            "ent_coef": self._ent_coef,
            "gamma": self._gamma,
            "lam": self._lam,
            "max_grad_norm": self._max_grad_norm,
        }

    def update(self, collector: TransitionCollector) -> Dict[str, float]:
        replay_buffer: TransitionReplayBuffer = collector.replay_buffer
        data_dict: Dict[str, torch.Tensor] = collector.replay_buffer.data_dict
        with torch.no_grad():
            last_values: torch.Tensor = self._policy.critic(data_dict["observations"][-1]).view(-1)
        returns = trainer_utils.compute_gae_returns(
            data_dict["rewards"],
            data_dict["values"],
            data_dict["dones"],
            last_values,
            self._gamma,
            self._lam,
        ).view(-1)
        # reshape data for computing loss
        observations = data_dict["observations"].view(
            replay_buffer.num_transitions_total, *collector.replay_buffer.obs_dim
        )
        next_observations = data_dict["next_observations"].view(
            replay_buffer.num_transitions_total, *collector.replay_buffer.obs_dim
        )
        rewards = data_dict["rewards"].view(replay_buffer.num_transitions_total)
        actions = data_dict["actions"].view(
            replay_buffer.num_transitions_total, *collector.env_wrapper.action_dim
        )
        exp_values = data_dict["values"].view(-1)
        advantages = returns - exp_values
        # update policy
        self._optimizer.zero_grad()
        logp_actions, values, entropies = self._policy.forward(observations, actions)
        values: torch.Tensor = values.view(-1)
        next_values: torch.Tensor = self._policy.forward_critic(next_observations).view(-1)
        actor_loss: torch.Tensor = -(logp_actions * advantages).mean()
        critic_loss: torch.Tensor = (rewards + self._gamma * next_values - values).pow(2).mean()
        entropy_loss: torch.Tensor = entropies.mean()
        total_loss = actor_loss + self._vf_coef * critic_loss - self._ent_coef * entropy_loss
        total_loss.backward()
        if self._max_grad_norm is not None:
            torch.nn.utils.clip_grad.clip_grad_norm_(self._policy.parameters(), self._max_grad_norm)
        self._optimizer.step()
        assert critic_loss is not None
        collector.clear()
        return {
            "policy/logp_a": torch.exp(logp_actions.detach()).mean().item(),
            "loss/actor_loss": actor_loss.detach().item(),
            "loss/critic_loss": critic_loss.detach().item(),
            "loss/entropy_loss": entropy_loss.detach().item(),
        }
