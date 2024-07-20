from typing import Callable, Dict, List, Optional, Tuple
import numpy as np
import torch
from rlvortex.algs import A2C
from rlvortex.policy import A2CPolicy
from rlvortex.collectors import TransitionCollector
from rlvortex.replay_buffer import TransitionReplayBuffer
import rlvortex.utils.trainer_utils as trainer_utils


class PPO(A2C):
    def __init__(
        self,
        *,
        policy: A2CPolicy,
        init_lr: float = 3e-4,
        lr_range: Tuple[float, float] = (1e-4, 1e-3),
        optimizer_fn: Callable = torch.optim.Adam,
        vf_coef: float = 0.5,
        ent_coef: float = 0.01,
        normalize_adv: bool = False,
        gamma: float = 0.998,
        lam: float = 0.95,
        max_grad_norm: Optional[float] = None,
        learning_iterations: int = 16,
        batch_size: int = 256,
        clip_ratio: float = 0.2,
        dual_clip_ratio: Optional[float] = None,
        value_loss_clip: bool = False,
        update_break: bool = True,
        desired_kl: Optional[float] = None,
    ) -> None:
        assert isinstance(policy, A2CPolicy), "policy must be an instance of PGPolicy"
        assert (
            isinstance(gamma, float) and 0.0 <= gamma <= 1.0
        ), "gamma must be a float number between 0.0 and 1.0, "
        super().__init__(
            policy=policy,
            init_lr=init_lr,
            optimizer_fn=optimizer_fn,
            vf_coef=vf_coef,
            ent_coef=ent_coef,
            gamma=gamma,
            lam=lam,
            max_grad_norm=max_grad_norm,
        )
        self._normalize_adv: bool = normalize_adv
        self._lr_range: Tuple[float, float] = lr_range
        self._learning_iterations: int = learning_iterations
        self._batch_size = batch_size
        self._clip_ratio: float = clip_ratio
        self._dual_clip_ratio: Optional[float] = dual_clip_ratio
        self._value_clip: bool = value_loss_clip
        self._update_break: bool = update_break
        self._desired_kl: Optional[float] = desired_kl

    @property
    def params(self) -> Dict:
        params_dict: Dict = super().params
        params_dict.update(
            {
                "name": self.__class__.__name__,
                "normalize_adv": self._normalize_adv,
                "lr_range": self._lr_range,
                "learning_iterations": self._learning_iterations,
                "batch_size": self._batch_size,
                "clip_ratio": self._clip_ratio,
                "dual_clip_ratio": self._dual_clip_ratio,
                "value_loss_clip": self._value_clip,
                "update_break": self._update_break,
                "desired_kl": self._desired_kl,
            }
        )
        return params_dict

    def update(self, collector: TransitionCollector) -> Dict[str, float]:
        from torch.utils.data.sampler import BatchSampler, SequentialSampler

        self.policy.train()
        replay_buffer: TransitionReplayBuffer = collector.replay_buffer
        data_dict: Dict[str, torch.Tensor] = replay_buffer.data_dict
        with torch.no_grad():
            last_values: torch.Tensor = self._policy.critic(data_dict["observations"][-1]).view(-1)
        returns_data = trainer_utils.compute_gae_returns(
            data_dict["rewards"],
            data_dict["values"],
            data_dict["dones"],
            last_values,
            self._gamma,
            self._lam,
        ).view(-1)
        # prepare data for computing loss
        observations_data = data_dict["observations"].view(
            replay_buffer.num_transitions_total, *collector.replay_buffer.obs_dim
        )
        actions_data = data_dict["actions"].view(
            replay_buffer.num_transitions_total, *collector.env_wrapper.action_dim
        )
        logp_actions_data = data_dict["logp_actions"].view(replay_buffer.num_transitions_total)
        values_data = data_dict["values"].view(-1)
        advantages_data = returns_data - values_data

        # update policy
        sampler: SequentialSampler = SequentialSampler(range(replay_buffer.num_transitions_total))
        minibatch_indices: BatchSampler = BatchSampler(sampler, self._batch_size, drop_last=True)
        # loss recorder
        pi_losses: List[float] = []
        v_losses: List[float] = []
        entropy_losses: List[float] = []
        approx_kl_divs: List[float] = []
        act_probs: List[float] = []
        for _ in range(self._learning_iterations):
            for indices in minibatch_indices:
                # fetch batch data
                actions_batch_data: torch.Tensor = actions_data[indices]
                logp_actions_batch_data: torch.Tensor = logp_actions_data[indices]
                observations_batch_data: torch.Tensor = observations_data[indices]
                values_batch_data: torch.Tensor = values_data[indices]
                returns_batch_data: torch.Tensor = returns_data[indices]
                advantages_batch_data: torch.Tensor = advantages_data[indices]
                if self._normalize_adv:
                    advantages_batch_data = (advantages_batch_data - advantages_batch_data.mean()) / (
                        advantages_batch_data.std() + 1e-8
                    )
                logp_actions, values, entropies = self._policy.forward(
                    observations_batch_data, actions_batch_data
                )

                # update learning ratio
                with torch.no_grad():
                    log_ratio = (logp_actions - logp_actions_batch_data).mean()
                    approx_kl_div = torch.mean(log_ratio.exp() - 1 - log_ratio).item()
                if self._update_lr(approx_kl_div):
                    break

                # compute losses
                self._optimizer.zero_grad()
                pi_loss: torch.Tensor = self._compute_pi_loss(
                    logp_actions, logp_actions_batch_data, advantages_batch_data
                )
                v_loss: torch.Tensor = self._compute_value_loss(
                    values, values_batch_data, returns_batch_data
                )
                entropy_loss: torch.Tensor = entropies.mean()
                total_loss: torch.Tensor = pi_loss + self._vf_coef * v_loss - self._ent_coef * entropy_loss

                # record log info
                pi_losses.append(pi_loss.detach().item())
                v_losses.append(v_loss.detach().item())
                entropy_losses.append(entropy_loss.detach().item())
                approx_kl_divs.append(approx_kl_div)
                act_probs.append(torch.exp(logp_actions.detach()).mean().item())

                # perform update
                total_loss.backward()
                if self._max_grad_norm is not None:
                    torch.nn.utils.clip_grad.clip_grad_norm_(self._policy.parameters(), self._max_grad_norm)
                self._optimizer.step()
        collector.clear()
        return {
            "collection/gae_returns": np.mean(returns_data.cpu().numpy()),
            "collection/advs": np.mean(advantages_data.cpu().numpy()),
            "loss/pi_loss": np.mean(pi_losses),
            "loss/v_loss": np.mean(v_losses),
            "loss/entropy_loss": np.mean(entropy_losses),
            "policy/approx_kl_div": np.mean(approx_kl_divs),
            "policy/action_prob": np.mean(act_probs),
            "policy/learning_rate": self._init_lr,
        }

    def _compute_pi_loss(
        self, logp_actions: torch.Tensor, logp_actions_data: torch.Tensor, advtanges_data: torch.Tensor
    ) -> torch.Tensor:
        policy_ratio: torch.Tensor = (logp_actions - logp_actions_data).exp()
        clipped_losses: torch.Tensor = (
            torch.clamp(policy_ratio, 1.0 - self._clip_ratio, 1.0 + self._clip_ratio) * advtanges_data
        )
        normal_losses: torch.Tensor = advtanges_data * policy_ratio
        pi_losses: torch.Tensor = -torch.min(normal_losses, clipped_losses)
        # perform dual clipping: https://arxiv.org/pdf/1912.09729.pdf
        if self._dual_clip_ratio:
            dual_clipped_pi_losses: torch.Tensor = self._dual_clip_ratio * -advtanges_data
            pi_loss: torch.Tensor = torch.where(advtanges_data < 0, dual_clipped_pi_losses, pi_losses).mean()
        else:
            pi_loss: torch.Tensor = pi_losses.mean()
        return pi_loss

    def _compute_value_loss(
        self, values: torch.Tensor, values_data: torch.Tensor, returns_data: torch.Tensor
    ) -> torch.Tensor:
        """
        # value loss clip: https://iclr-blog-track.github.io/2022/03/25/ppo-implementation-details/ -> Value Function Loss Clipping (ppo2/model.py#L68-L75)

        Value Function Loss Clipping (ppo2/model.py#L68-L75) Code-level Optimizations
        PPO clips the value function like the PPO’s clipped surrogate objective. Given the V_{targ} = returns = advantages + values, PPO fits the the value network by minimizing the following loss:

        LV=max[(Vθt−Vtarg)2,(clip(Vθt,Vθt−1−ε,Vθt−1+ε)−Vtarg)2]
        Engstrom, Ilyas, et al., (2020) find no evidence that the value function loss clipping helps with the performance. Andrychowicz, et al. (2021) suggest value function loss clipping even hurts performance (decision C13, figure 43).
        We implemented this detail because this work is more about high-fidelity reproduction of prior results.
        """  # noqa: E501
        if self._value_clip:
            clipped_values = values_data + (values - values_data).clamp(-self._clip_ratio, self._clip_ratio)
            clipped_value_losses = (clipped_values - returns_data).pow(2)
            normal_value_losses = (values - returns_data).pow(2)
            value_loss = torch.max(normal_value_losses, clipped_value_losses).mean()
        else:
            value_loss = (values - returns_data).pow(2).mean()
        return value_loss

    def _update_lr(self, approx_kl_div: float) -> bool:
        if self._desired_kl:
            """
            https://iclr-blog-track.github.io/2022/03/25/ppo-implementation-details/
            approxkl: the approximate Kullback–Leibler divergence, measured by (-logratio).mean(), which corresponds to the k1 estimator in John Schulman’s blog post on approximating KL divergence. This blog post also suggests using an alternative estimator ((ratio - 1) - logratio).mean(), which is unbiased and has less variance.

            """  # noqa: E501
            if approx_kl_div > self._desired_kl * 1.5 and self._update_break:
                return True
            if approx_kl_div > self._desired_kl * 2.0:
                self._init_lr = max(self._init_lr / 1.5, self._lr_range[0])
            elif approx_kl_div < self._desired_kl / 2.0 and approx_kl_div > 0.0:
                self._init_lr = min(self._init_lr * 1.5, self._lr_range[1])
            for param_group in self._optimizer.param_groups:
                param_group["lr"] = self._init_lr
        return False
