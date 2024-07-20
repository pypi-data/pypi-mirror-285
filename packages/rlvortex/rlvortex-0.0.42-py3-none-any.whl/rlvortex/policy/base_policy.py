import abc
from typing import Dict, Tuple
import torch
import rlvortex.policy.ppo_policy as ppo_policy
from rlvortex.policy.quick_build import init_weights


class BasePolicy(torch.nn.Module):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()

    @property
    @abc.abstractmethod
    def params(self) -> Dict:
        raise NotImplementedError

    @abc.abstractmethod
    def forward(self, *args, **kwargs):
        """
        Define  the forward pass of the policy.
        This method is used to compute the loss. Graident is computed.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def step(self, *args, **kwargs) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:
        """
        This method is used to interact with the environment for experience collection.
        Return: action, Dict of extra information
        No gradient is computed.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def act(self, *args, **kwargs):
        """
        This method is used to interact with the environment for evaluation by trained model.
        """
        raise NotImplementedError


class PGPolicy(BasePolicy):
    def __init__(self, *, model: ppo_policy.BaseActorModule) -> None:
        super().__init__()
        assert isinstance(model, torch.nn.Module), "model must be an instance of Module"
        self.model: ppo_policy.BaseActorModule = model

    def step(self, observations: torch.Tensor) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:
        return self.act(observations), {}

    def act(self, observations: torch.Tensor) -> torch.Tensor:
        with torch.no_grad():
            pi: torch.distributions.Distribution = self.model._distribution(observations)
            action: torch.Tensor = pi.sample()
        return action

    def forward(self, observations: torch.Tensor, actions: torch.Tensor) -> torch.Tensor:
        pi: torch.distributions.Distribution = self.model._distribution(observations)
        logp_a: torch.Tensor = self.model._log_prob_from_distribution(pi=pi, act=actions)
        return logp_a


class A2CPolicy(BasePolicy):
    def __init__(self, *, actor: ppo_policy.BaseActorModule, critic: ppo_policy.BaseCriticModule) -> None:
        super().__init__()
        assert isinstance(actor, torch.nn.Module), "actor must be an instance of Module"
        assert isinstance(critic, torch.nn.Module), "critic must be an instance of Module"
        self.actor: ppo_policy.BaseActorModule = actor
        self.critic: ppo_policy.BaseCriticModule = critic

    def step(self, observations: torch.Tensor) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:
        with torch.no_grad():
            pis: torch.distributions.Distribution = self.actor._distribution(observations)
            actions: torch.Tensor = pis.sample()
            logp_actions: torch.Tensor = self.actor._log_prob_from_distribution(pi=pis, act=actions)
            values: torch.Tensor = self.critic(observations).view(-1)
        return actions, {"values": values, "logp_actions": logp_actions}

    def act(self, observations: torch.Tensor) -> torch.Tensor:
        with torch.no_grad():
            pis: torch.distributions.Distribution = self.actor._distribution(observations)
            actions: torch.Tensor = pis.sample()
        return actions

    def _forward_actor(
        self, observations: torch.Tensor, actions: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        pis: torch.distributions.Distribution = self.actor._distribution(observations)
        logp_actions: torch.Tensor = self.actor._log_prob_from_distribution(pi=pis, act=actions)
        return logp_actions, pis.entropy().mean()

    def forward_critic(self, observations: torch.Tensor) -> torch.Tensor:
        values: torch.Tensor = self.critic(observations).view(-1)
        return values

    def forward(
        self, observations: torch.Tensor, actions: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        logp_actions, entropies = self._forward_actor(observations, actions)
        values = self.forward_critic(observations)
        return logp_actions, values, entropies
