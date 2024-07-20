import os
from typing import List, Optional, Callable
import numpy as np
import torch
from rlvortex.envs.base_env import EnvWrapper
from rlvortex.replay_buffer.ppo_replay_buffer import (
    TensorPPOReplayBuffer,
)
from rlvortex.policy.ppo_policy import BasePPOPolicy
from rlvortex.trainer.base_trainer import BaseTrainer
from rlvortex.utils import vlogger


class NativePPOTrainer(BaseTrainer):
    def __init__(
        self,
        *,
        env: EnvWrapper,
        policy: BasePPOPolicy,
        optimizer: Callable,
        steps_per_env=2048,
        learning_iterations=10,
        num_batches_per_env: int = 32,
        init_lr: float = 3e-4,
        lr_range: List[float] = [1e-5, 1e-3],  # min, max
        val_loss_coef: float = 0.5,
        normalize_adv: bool = True,
        clip_ratio: float = 0.2,
        dual_clip_ratio: Optional[float] = None,
        gamma: float = 0.998,
        lam: float = 0.95,
        entropy_loss_coef=0.0,
        max_grad_norm: Optional[float] = 0.5,
        val_loss_clip=False,
        desired_kl=None,
        update_break: bool = False,
        random_sampler: bool = False,
        trainer_dir: str = os.path.join(os.getcwd(), "ppo_trainers"),
        enable_tensorboard: bool = False,
        save_freq: int = -1,  # if save_freg == -1, then disable save, if save_freq == 0, then save at the end of training,otherwise save every save_freq epochs  # noqa: E501
        log_type: vlogger.LogType = vlogger.LogType.Screen,
        device: torch.device = torch.device("cpu"),
        comment: str = "",
        seed: int = 19970314,
    ) -> None:
        super().__init__(
            env=env,
            policy=policy,
            optimizer=optimizer,
            init_lr=init_lr,
            steps_per_env=steps_per_env,
            trainer_dir=trainer_dir,
            enable_tensorboard=enable_tensorboard,
            save_freq=save_freq,
            log_type=log_type,
            comment=comment,
            seed=seed,
            device=device,
        )
        # store input parameters
        self.learning_iterations = learning_iterations
        self.num_batches_per_env = num_batches_per_env
        self.lr_range = lr_range
        self.val_loss_coef = val_loss_coef
        self.normalize_adv = normalize_adv
        self.clip_ratio = clip_ratio
        self.dual_clip_ratio: Optional[float] = dual_clip_ratio
        self.gamma = gamma
        self.lam = lam
        self.entropy_loss_coef = entropy_loss_coef
        self.max_grad_norm: Optional[float] = max_grad_norm
        self.val_loss_clip = val_loss_clip
        self.desired_kl = desired_kl
        self.update_break = update_break
        self.random_sampler = random_sampler

        # init variables
        self.replay_buffer: TensorPPOReplayBuffer = TensorPPOReplayBuffer(
            num_envs=1,
            steps_per_env=self.steps_per_env,
            observation_dim=self.env.observation_dim,
            action_dim=self.env.action_dim,
            random_sampler=self.random_sampler,
            device=self.device,
        )

    def train(self, epochs: int):
        self.logger.info_dict(self.params)
        self.env.awake()
        o, _ = self.env.reset()
        ep_ret = 0
        ep_len = 0
        for _ in range(epochs):
            self.clear_ep_info()
            self.clear_customized_tb_info()
            for t in range(self.steps_per_env):
                a, v, logp_a = self.policy.step(
                    torch.as_tensor(o, dtype=torch.float32, device=self.device)
                )  # in torch.Tensor,no gradient computed
                # print(a, v, logp_a)
                # import pdb

                # pdb.set_trace()
                next_o, r, d, cache = self.env.step(a)

                ep_len += 1
                ep_ret += r
                self.replay_buffer.append_transitions(
                    a,
                    torch.as_tensor(o, dtype=torch.float32, device=self.device),
                    torch.as_tensor(r, dtype=torch.float32, device=self.device),
                    torch.as_tensor(d, dtype=torch.float32, device=self.device),
                    v,
                    logp_a,
                )
                o = next_o
                if d:
                    self.sample_steps += ep_len
                    self.append_episode_rollout_info(ep_length=ep_len, ep_return=ep_ret)
                    (o, _), (ep_len, ep_ret) = self.env.reset(), (0, 0)
                self.append_customized_tb_info(cache)
            _, v, _ = self.policy.step(torch.as_tensor(o, dtype=torch.float32, device=self.device))
            self.replay_buffer.compute_returns(v, self.gamma, self.lam)
            self.__update_policy()
            self._log_all(self.epoch)
            if (self.save_freq != -1 and self.epoch % self.save_freq == 0) or self.epoch == epochs - 1:
                tmp_rtn = (
                    -1
                    if self.log_buffer_size == 0
                    else np.mean(self.info_buffer["rollout"]["episode_return"]).astype(int)
                )
                model_path = os.path.join(
                    self.trainer_monitor_table.save_path,
                    f"{self.epoch}_{tmp_rtn}.pth",
                )
                torch.save(self.policy, model_path)
                self.saved_model_paths.append(model_path)
            self.replay_buffer.clear()
            self.epoch += 1

    def destory(self):
        self.env.destory()
        self.net = None
        del self.net

    @property
    def params(self):
        return {
            "gamma": self.gamma,
            "lam": self.lam,
            "steps_per_env": self.steps_per_env,
            "entropy_loss_coef": self.entropy_loss_coef,
            "max_grad_norm": self.max_grad_norm,
            "use_clipped_value_loss": self.val_loss_clip,
            "desired_kl": self.desired_kl,
            "sampler": self.random_sampler,
            "save_freq": self.save_freq,
        }

    def __update_policy(self):
        batches_indices = self.replay_buffer.mini_batch_generator(self.num_batches_per_env)
        (
            act_data,
            obs_data,
            adv_data,
            ret_data,
            val_data,
            act_logp_data,
        ) = self.replay_buffer.tensor_data(self.device)
        for _ in range(self.learning_iterations):
            for indices in batches_indices:
                old_act = act_data[indices]
                old_obs = obs_data[indices]
                old_val = val_data[indices]
                old_act_logp = act_logp_data[indices]
                ret = ret_data[indices]
                adv = adv_data[indices]
                # normalize advantages
                if self.normalize_adv:
                    adv = (adv - adv.mean()) / (adv.std() + 1e-8)
                # compute values for policy and value loss
                act_logp, val, entropy = self.policy(old_act, old_obs)
                # compute pi loss
                policy_ratio = torch.exp(act_logp - old_act_logp)
                losses = adv * policy_ratio
                # perform normal ppo clipping
                clipped_losses = torch.clamp(policy_ratio, 1 - self.clip_ratio, 1 + self.clip_ratio) * adv
                pi_losses = -torch.min(losses, clipped_losses)

                # perform dual clipping: https://arxiv.org/pdf/1912.09729.pdf
                if self.dual_clip_ratio:
                    dual_clipped_pi_losses = self.dual_clip_ratio * -adv
                    pi_loss = torch.where(adv < 0, dual_clipped_pi_losses, clipped_losses).mean()
                else:
                    pi_loss = pi_losses.mean()
                # compute value loss
                """
                # value loss clip: https://iclr-blog-track.github.io/2022/03/25/ppo-implementation-details/ -> Value Function Loss Clipping (ppo2/model.py#L68-L75)

                Value Function Loss Clipping (ppo2/model.py#L68-L75) Code-level Optimizations
                PPO clips the value function like the PPO’s clipped surrogate objective. Given the V_{targ} = returns = advantages + values, PPO fits the the value network by minimizing the following loss:

                LV=max[(Vθt−Vtarg)2,(clip(Vθt,Vθt−1−ε,Vθt−1+ε)−Vtarg)2]
                Engstrom, Ilyas, et al., (2020) find no evidence that the value function loss clipping helps with the performance. Andrychowicz, et al. (2021) suggest value function loss clipping even hurts performance (decision C13, figure 43).
                We implemented this detail because this work is more about high-fidelity reproduction of prior results.
                """  # noqa: E501
                if self.val_loss_clip:
                    values_clipped = old_val + (val - old_val).clamp(-self.clip_ratio, self.clip_ratio)
                    val_losses = (val - ret).pow(2)
                    clipped_val_losses = (values_clipped - ret).pow(2)
                    value_loss = torch.max(val_losses, clipped_val_losses).mean()
                else:
                    value_loss = (ret - val.squeeze(1)).pow(2).mean()

                actor_loss = pi_loss - self.entropy_loss_coef * entropy
                # compute kl divergence and adaptively adjust learning rate
                log_ratio = (act_logp - old_act_logp).mean()
                approx_kl_div = torch.mean((torch.exp(log_ratio) - 1) - log_ratio)
                if self.desired_kl:
                    """
                    https://iclr-blog-track.github.io/2022/03/25/ppo-implementation-details/
                    approxkl: the approximate Kullback–Leibler divergence, measured by (-logratio).mean(), which corresponds to the k1 estimator in John Schulman’s blog post on approximating KL divergence. This blog post also suggests using an alternative estimator ((ratio - 1) - logratio).mean(), which is unbiased and has less variance.

                    """  # noqa: E501
                    if approx_kl_div > self.desired_kl * 1.5 and self.update_break:
                        break
                    if approx_kl_div > self.desired_kl * 2.0:
                        self.learning_rate = max(self.learning_rate / 1.5, self.lr_range[0])
                    elif approx_kl_div < self.desired_kl / 2.0 and approx_kl_div > 0.0:
                        self.learning_rate = min(self.learning_rate * 1.5, self.lr_range[1])
                # compute gradient and do update step
                loss = actor_loss + self.val_loss_coef * value_loss
                self.policy_optimizer.zero_grad()
                loss.backward()
                # Clip grad norm
                if self.max_grad_norm:
                    torch.nn.utils.clip_grad.clip_grad_norm_(
                        self.policy.actor.parameters(), self.max_grad_norm
                    )
                    torch.nn.utils.clip_grad.clip_grad_norm_(
                        self.policy.critic.parameters(), self.max_grad_norm
                    )
                self.policy_optimizer.step()
                # append log info
                self.append_trainer_info(
                    total_loss=actor_loss.item() + value_loss.item(),
                    pi_loss=pi_loss.item(),
                    v_loss=value_loss.item(),
                    entropy_loss=entropy.item(),
                    kl_div=approx_kl_div.item(),
                    learning_rate=self.learning_rate,
                    act_prob=torch.exp(act_logp).mean().item(),
                )
