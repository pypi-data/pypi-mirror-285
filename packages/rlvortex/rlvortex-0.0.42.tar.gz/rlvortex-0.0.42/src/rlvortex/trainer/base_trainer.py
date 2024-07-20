import os
import abc
from datetime import datetime
from collections import namedtuple, deque
from typing import Any, Dict, Optional, Callable, Union
import torch
from torch.utils.tensorboard.writer import SummaryWriter
import numpy as np
from rlvortex.algs import BaseRLAlgorithm
from rlvortex.collectors import BaseCollector
from rlvortex.envs.base_env import EnvWrapper
from rlvortex.utils import vlogger
from rlvortex.policy.ppo_policy import BasePPOPolicy


class BaseTrainerR(abc.ABC):
    """
    BaseTrainerR is a base class for all trainers, who is responsible for
    1) the interaction between the environment and the policy
    2) the training and evalution process of the policy
    3) the logging and saving of the training process
    """

    def __init__(
        self,
        *,
        collector: BaseCollector,
        algorithm: BaseRLAlgorithm,
        flow_logger: vlogger.FlowLogger,
        save_interval: int,
        save_path: os.PathLike,
        device: torch.device,
    ) -> None:
        assert isinstance(algorithm, BaseRLAlgorithm), "algorithm must be an instance of BaseAlgorithm"
        assert isinstance(device, torch.device), "device must be an instance of torch.device"
        self.algorithm: BaseRLAlgorithm = algorithm
        self.collector: BaseCollector = collector
        self.flow_meter: vlogger.BaseFlowMeter = vlogger.BaseFlowMeter(flow_logger)
        self.collector.borrow_flow_meter(self.flow_meter)
        self._save_info: Dict[str, Any] = {
            "save_interval": save_interval,
            "save_path": save_path,
            "best_return": float("-inf"),
            "best_epoch": 0,
        }
        self.epoch: int = 0
        self._device: torch.device = device

    @property
    @abc.abstractmethod
    def params(self) -> Dict:
        return {
            "algorithm": self.algorithm.params,
            "collector": self.collector.params,
            "device": self._device.type,
        }

    @abc.abstractmethod
    def train(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def save(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def evaluate(self, *args, **kwargs):
        raise NotImplementedError


class OnPolicyTrainer(BaseTrainerR):
    """
    the implement of Policy Gradient Trainer & Algorithm is referenced from
    openai spinning up: https://spinningup.openai.com/en/latest/spinningup/rl_intro3.html

    we use a different way of computing the return R_t(/tau)
    1.  we use the the last reward to compute the return of the last state, instead of
        waiting the end of the eposide.
    2. this different may cause some bias of the expected return

    """

    def __init__(
        self,
        *,
        collector: BaseCollector,
        algorithm: BaseRLAlgorithm,
        flow_logger: vlogger.FlowLogger,
        save_interval: int,
        save_path: os.PathLike,
        device: torch.device,
    ) -> None:
        super().__init__(
            collector=collector,
            algorithm=algorithm,
            flow_logger=flow_logger,
            save_interval=save_interval,
            save_path=save_path,
            device=device,
        )
        self.env_wrapper = self.collector.env_wrapper

    @property
    def params(self) -> Dict[str, Any]:
        return super().params

    def train(self, epochs: int):
        self._on_training_start()
        self.flow_meter.init()
        self.flow_meter.logger.board_dict(self.params)
        for epoch in range(epochs):
            self._on_collection_start(epoch)
            self.collector.collect()
            self._on_collection_end(epoch)
            self._on_policy_update_start(epoch)
            update_data: Dict[str, torch.Tensor] = self.algorithm.update(self.collector)
            self._on_policy_update_end(epoch)
            self.flow_meter.store_epoch_data(update_data)
            self.save(self.epoch, self.flow_meter.episode_return)
            self.flow_meter.log()
            self.flow_meter.reset()
            self.epoch += 1

    def _on_training_start(self) -> None:
        """
        This method is called at the beginning of the training (before the update loop).
        """
        pass

    def _on_collection_start(self, epoch: int) -> None:
        """
        This method is called before the collection of environment interaction using the current policy.
        This event is triggered before collecting new samples at each update loop.
        """
        pass

    def _on_collection_end(self, epoch: int) -> None:
        """
        This method is called after the collection of environment interaction using the current policy.
        This event is triggered after collecting new samples at each update loop.
        """
        pass

    def _on_policy_update_start(self, epoch: int) -> None:
        """
        This event is triggered before the policy update.
        """
        pass

    def _on_policy_update_end(self, epoch: int) -> None:
        """
        This event is triggered after the policy update.
        """
        pass

    def save(self, epoch: int, save_return: float):
        if self._save_info["save_interval"] == -1:
            return
        if not os.path.exists(self._save_info["save_path"]):
            os.mkdir(self._save_info["save_path"])

        if epoch > -1 and epoch % self._save_info["save_interval"] == 0:
            torch.save(
                self.algorithm.policy,
                os.path.join(self._save_info["save_path"], f"tmp_{epoch}_{save_return:.2f}.pth"),
            )
            if save_return >= self._save_info["best_return"]:
                self._save_info["best_return"] = save_return
                self._save_info["best_epoch"] = epoch
                torch.save(
                    self.algorithm.policy,
                    os.path.join(
                        self._save_info["save_path"],
                        f"best_{self.flow_meter.logger.comment}_{epoch}_{save_return:.2f}.pth",
                    ),
                )

    def evaluate(self, num_eposides: int, env_wrapper: Optional[EnvWrapper] = None):
        if env_wrapper is None:
            env_wrapper = self.env_wrapper
        else:
            env_wrapper = env_wrapper.awake()
        assert (
            env_wrapper.num_envs == 1
        ), "only support single env for evaluation, but get {env_wrapper.num_envs} envs"
        observations, _ = env_wrapper.reset()
        num_envs = env_wrapper.env.num_envs
        ep_lens, ep_returns = [], []
        ep_len, ep_return = np.zeros(num_envs), np.zeros(num_envs)
        eposides = 0
        self.algorithm.policy.eval()
        while eposides != num_eposides:
            actions = self.algorithm.policy.act(observations)
            next_observations, rewards, dones, _ = env_wrapper.step(actions)
            ep_return += rewards.cpu().numpy()
            ep_len += 1
            if torch.any(dones):
                done_indices = torch.where(dones)
                reset_indcies = done_indices[0].cpu().tolist()
                reset_observations, _ = env_wrapper.reset(reset_indcies)
                next_observations[done_indices] = reset_observations
                ep_returns.extend(ep_return[reset_indcies])
                ep_lens.extend(ep_len[reset_indcies])
                ep_return[reset_indcies], ep_len[reset_indcies] = 0, 0
                eposides += 1
            observations = next_observations
        if len(ep_returns) > 0:
            self.flow_meter.logger.info(
                f"evalution result: ep_len: {np.mean(ep_lens)}, ep_return: {np.mean(ep_returns)}"
            )  # noqa: E501
        return np.mean(ep_returns) if len(ep_returns) > 0 else 0


TrainerMonitorTable = namedtuple(
    "TrainMonitorTale",
    [
        "start_time",
        "start_time_str",
        "trainer_dir",
        "trainer_name",
        "trainer_path",
        "tensorboard_path",
        "save_path",
        "log_path",
    ],
)


class BaseTrainer(abc.ABC):
    def __init__(
        self,
        *,
        env: EnvWrapper,
        policy: BasePPOPolicy,
        optimizer: Callable,
        init_lr: float,
        steps_per_env: int,
        device: torch.device,
        trainer_dir: str,
        enable_tensorboard: bool,
        save_freq: int,  # if save_freg == -1, then disable save, if save_freq == 0, then save at the end of training,otherwise save every save_freq epochs  # noqa: E501
        log_type: vlogger.LogType,
        comment: str,
        seed: int,
    ) -> None:
        self.env: EnvWrapper = env
        self.steps_per_env: int = steps_per_env
        self.steps: int = 0
        self.epoch: int = 0
        self.device: torch.device = device
        self.policy: BasePPOPolicy = policy.to(self.device)

        self._learning_rate: float = init_lr
        self.policy_optimizer: Callable = optimizer(self.policy.parameters(), lr=init_lr)
        self.save_freq: int = save_freq
        self.enable_tensorboard: bool = enable_tensorboard
        self.log_type: vlogger.LogType = log_type
        self.comment: str = comment
        self.seed: int = seed
        # log and save
        start_time = datetime.now()
        start_time_str = start_time.strftime("%Y-%m-%d_%H-%M-%S")
        trainer_name = f"ppo_trainer_{start_time_str}_cmt_{self.comment}"
        trainer_path = os.path.join(trainer_dir, trainer_name)
        self.trainer_monitor_table: TrainerMonitorTable = TrainerMonitorTable(
            start_time=start_time,
            start_time_str=start_time_str,
            trainer_dir=trainer_dir,
            trainer_name=trainer_name,
            trainer_path=os.path.join(trainer_path),
            save_path=os.path.join(trainer_path, "models"),
            tensorboard_path=os.path.join(trainer_path, "runs"),
            log_path=os.path.join(trainer_path, "trainer.log"),
        )
        self.__gen_trainer_dirs_and_tb()
        self.logger: vlogger.VLogger = vlogger.VLogger(
            log_type=self.log_type,
            log_path=self.trainer_monitor_table.log_path,
        )
        self.info_buffer = {
            "rollout": {
                "eposide_return": [],
                "eposide_length": [],
                "moving_avg_return_100": deque(maxlen=100),
                "moving_avg_length_100": deque(maxlen=100),
            },
            "trainer": {
                "total_loss": [],
                "pi_loss": [],
                "v_loss": [],
                "entropy_loss": [],
                "kl_div": [],
                "learning_rate": [],
                "act_prob": [],
            },
        }

        self.sample_steps = 0
        self.log_buffer_size = 0
        self.customized_log_info = {}
        self.customized_tb_info = {}
        self.saved_model_paths = []

    def _update_learning_rate(self):
        for param_group in self.policy_optimizer.param_groups:
            param_group["lr"] = self._learning_rate

    def __gen_trainer_dirs_and_tb(self):
        if not self.log_type.File and not self.enable_tensorboard and not self.save_freq:
            return
        if not os.path.exists(self.trainer_monitor_table.trainer_dir):
            os.mkdir(self.trainer_monitor_table.trainer_dir)
        if not os.path.exists(self.trainer_monitor_table.trainer_path):
            os.mkdir(self.trainer_monitor_table.trainer_path)
        if self.save_freq and not os.path.exists(self.trainer_monitor_table.save_path):
            os.mkdir(self.trainer_monitor_table.save_path)
        if self.enable_tensorboard:
            self._tb_writer = SummaryWriter(
                self.trainer_monitor_table.tensorboard_path,
                comment=self.trainer_monitor_table.trainer_name,
            )

    def append_episode_rollout_info(
        self,
        *,
        ep_return: Union[float, torch.Tensor],
        ep_length: Union[float, torch.Tensor],
    ):
        # import pdb
        # pdb.set_trace()
        if isinstance(ep_return, torch.Tensor):
            ep_return = ep_return.cpu().numpy()
        if isinstance(ep_length, torch.Tensor):
            ep_length = ep_length.cpu().numpy()
        self.info_buffer["rollout"]["eposide_return"].append(ep_return)
        self.info_buffer["rollout"]["eposide_length"].append(ep_length)
        self.info_buffer["rollout"]["moving_avg_return_100"].append(ep_return)
        self.info_buffer["rollout"]["moving_avg_length_100"].append(ep_length)
        if self.enable_tensorboard:
            self._tb_writer.add_scalar("eposide/return", ep_return, self.sample_steps)
            self._tb_writer.add_scalar("eposide/length", ep_length, self.sample_steps)

        self.log_buffer_size += 1

    def append_trainer_info(
        self,
        *,
        total_loss: float,
        pi_loss: float,
        v_loss: float,
        entropy_loss: float,
        kl_div: float,
        learning_rate: float,
        act_prob: float,
    ):
        self.info_buffer["trainer"]["total_loss"].append(total_loss)
        self.info_buffer["trainer"]["pi_loss"].append(pi_loss)
        self.info_buffer["trainer"]["v_loss"].append(v_loss)
        self.info_buffer["trainer"]["entropy_loss"].append(entropy_loss)
        self.info_buffer["trainer"]["kl_div"].append(kl_div)
        self.info_buffer["trainer"]["learning_rate"].append(learning_rate)
        self.info_buffer["trainer"]["act_prob"].append(act_prob)

    def clear_ep_info(self):
        self.info_buffer["rollout"]["eposide_return"] = []
        self.info_buffer["rollout"]["eposide_length"] = []
        self.info_buffer["trainer"]["total_loss"] = []
        self.info_buffer["trainer"]["pi_loss"] = []
        self.info_buffer["trainer"]["v_loss"] = []
        self.info_buffer["trainer"]["entropy_loss"] = []
        self.info_buffer["trainer"]["kl_div"] = []
        self.info_buffer["trainer"]["learning_rate"] = []
        self.info_buffer["trainer"]["act_prob"] = []
        self.log_buffer_size = 0

    def _record_info_buffer(self, epoch: int):
        steps = self.steps_per_env * epoch
        if self.log_buffer_size > 0:
            rtn_mean, rtn_max, rtn_min, rtn_std = (
                np.mean(self.info_buffer["rollout"]["eposide_return"]),
                np.max(self.info_buffer["rollout"]["eposide_return"]),
                np.min(self.info_buffer["rollout"]["eposide_return"]),
                np.std(self.info_buffer["rollout"]["eposide_return"]),
            )

            len_mean, len_max, len_min, len_std = (
                np.mean(self.info_buffer["rollout"]["eposide_length"]),
                np.max(self.info_buffer["rollout"]["eposide_length"]),
                np.min(self.info_buffer["rollout"]["eposide_length"]),
                np.std(self.info_buffer["rollout"]["eposide_length"]),
            )
        else:
            (
                rtn_mean,
                rtn_max,
                rtn_min,
                rtn_std,
                len_mean,
                len_max,
                len_min,
                len_std,
            ) = (
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
            )
            self.info_buffer["rollout"]["moving_avg_return_100"].append(0.0)
            self.info_buffer["rollout"]["moving_avg_length_100"].append(0.0)
        total_loss = np.mean(self.info_buffer["trainer"]["total_loss"])
        pi_loss = np.mean(self.info_buffer["trainer"]["pi_loss"])
        v_loss = np.mean(self.info_buffer["trainer"]["v_loss"])
        entropy_loss = np.mean(self.info_buffer["trainer"]["entropy_loss"])
        kl_div = np.mean(self.info_buffer["trainer"]["kl_div"])
        lr = np.mean(self.info_buffer["trainer"]["learning_rate"])
        act_prob = np.mean(self.info_buffer["trainer"]["act_prob"])
        log_buffer = {
            "epoch": epoch,
            "steps": steps,
            "rollout": {
                "avg_ep_return": f"mean: {rtn_mean:.4f},max: {rtn_max:.4f}, min: {rtn_min:.4f}, std: {rtn_std:.4f}",  # noqa: E501
                "avg_ep_length": f"mean: {len_mean:.4f},max: {len_max:.4f}, min: {len_min:.4f}, std: {len_std:.4f}",  # noqa: E501
            },
            "trainer": {
                "total_loss": f"{total_loss:.4f}",
                "pi_loss": f"{pi_loss:.4f}",
                "v_loss": f"{v_loss:.4f}",
                "entropy_loss": f"{entropy_loss:.4f}",
                "kl_div": f"{kl_div:.4f}",
                "learning_rate": f"{lr:.4f}",
                "act_prob": f"{act_prob:.4f}",
            },
        }
        self.logger.info_dict(log_buffer)
        if self.enable_tensorboard:
            self._tb_writer.add_scalar("epoch_avg/return", rtn_mean, steps)
            self._tb_writer.add_scalar("epoch_avg/length", len_mean, steps)
            self._tb_writer.add_scalar(
                "moving_avg_100/return",
                np.mean(self.info_buffer["rollout"]["moving_avg_return_100"]),
                steps,
            )
            self._tb_writer.add_scalar(
                "moving_avg_100/length",
                np.mean(self.info_buffer["rollout"]["moving_avg_length_100"]),
                steps,
            )
            self._tb_writer.add_scalar("trainer/total_loss", total_loss, steps)
            self._tb_writer.add_scalar("trainer/pi_loss", pi_loss, steps)
            self._tb_writer.add_scalar("trainer/v_loss", v_loss, steps)
            self._tb_writer.add_scalar("trainer/entropy_loss", entropy_loss, steps)
            self._tb_writer.add_scalar("trainer/kl_div", kl_div, steps)
            self._tb_writer.add_scalar("trainer/learning_rate", self.learning_rate, steps)
            self._tb_writer.add_scalar("trainer/act_prob", act_prob, steps)

    def clear_customized_tb_info(self):
        self.customized_tb_info = {}

    def append_customized_tb_info(self, info: dict):
        for key, val in info.items():
            if key in self.customized_tb_info:
                self.customized_tb_info[key].append(val)
            else:
                self.customized_tb_info[key] = []

    def _log_customized_info(self):
        if len(self.customized_log_info.keys()) > 0:
            self.logger.info_dict(self.customized_log_info)

    def _tb_customized_info(self, epoch: int):
        return
        for key, val in self.customized_tb_info.items():
            print(key, val)
            self._tb_writer.add_scalar(f"customized/{key}_mean", np.mean(val), epoch * self.steps_per_env)

    def _log_all(self, epoch: int):
        self._record_info_buffer(epoch)
        self._log_customized_info()
        self._tb_customized_info(epoch)

    def get_saved_model_pathes(self):
        return self.saved_model_paths

    def train(self):
        raise NotImplementedError

    def evaluate(self, eposides: int = -1, env: Optional[EnvWrapper] = None):
        ext_env = env is not None
        ep_rtns = []
        ep_lens = []
        if not ext_env:
            env = self.env
        current_eposide = 0
        while current_eposide != eposides:
            env.awake()
            o, _ = env.reset()
            d = False
            ep_ret = 0
            ep_len = 0
            while not d:
                a = self.policy.act(
                    torch.as_tensor(o, dtype=torch.float32, device=self.device)
                )  # in torch.Tensor,no gradient computed
                next_o, r, d, cache = env.step(a)
                o = next_o
                ep_len += 1
                ep_ret += r

            ep_rtns.append(ep_ret)
            ep_lens.append(ep_len)
            current_eposide += 1

        if ext_env:
            env.destory()
        else:
            env.reset()
        return np.mean(ep_rtns), np.mean(ep_lens)

    @property
    def learning_rate(self):
        return self._learning_rate

    @learning_rate.setter
    def learning_rate(self, lr: float):
        self._learning_rate = lr
        for param_group in self.policy_optimizer.param_groups:
            param_group["lr"] = self.learning_rate
