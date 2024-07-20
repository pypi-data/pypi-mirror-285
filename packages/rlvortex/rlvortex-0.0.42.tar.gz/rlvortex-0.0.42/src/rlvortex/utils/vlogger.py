import os
import enum
import json
from datetime import datetime, timezone
import sys
from typing import Any, Deque, Dict, Optional, List, Union
from loguru import logger as loguru
import numpy as np
import torch
from torch.utils.tensorboard.writer import SummaryWriter
from collections import defaultdict, deque


class LogType(enum.Enum):
    Vanish = 1
    Screen = 2
    File = 3
    Board = 4


class FlowLogger:
    def __init__(
        self,
        log_types: List[LogType],
        log_path: Optional[os.PathLike],
        board_dir: Optional[os.PathLike],
        comment: Optional[str],
    ) -> None:
        self.__mute: bool = len(log_types) == 0
        self.__screen: bool = LogType.Screen in log_types
        self.__file: bool = LogType.File in log_types
        self.__board: bool = LogType.Board in log_types
        self.comment = "" if comment is None else comment

        self.__log_path: Optional[os.PathLike] = log_path
        self.__board_dir: Optional[os.PathLike] = board_dir
        if self.__screen:
            loguru.remove()
            loguru.add(
                sys.stdout,
                colorize=True,
                format="<green>{time:DD-MM-YYYY HH:mm:ss}</green> | <light-blue>{message}</light-blue>",
            )
        if self.__file:
            assert self.__log_path is not None, "log_path must be provided when log_type is File"
            loguru.remove()
            loguru.add(str(self.__log_path))
        if self.__board:
            assert self.__board_dir is not None, "board_dir must be provided when log_type is Board"

    def _init_board(self):
        self.__writer = SummaryWriter(os.path.join(str(self.__board_dir)))

    def info(self, msg: str):
        if self.__mute:
            return
        if self.__file or self.__screen:
            loguru.info(msg)

    def info_dict(self, dict_info: Dict[str, Any]):
        if self.__mute:
            return
        if self.__file or self.__screen:
            loguru.info(json.dumps(dict_info, sort_keys=False, indent=4))

    def board_dict(self, hp_dict: Dict[str, Any]):
        if self.__board:
            json_str = json.dumps(hp_dict, sort_keys=False, indent=4)
            json_str = "".join("\t" + line for line in json_str.splitlines(True))
            self.__writer.add_text("hyperparams", json_str, 0)

    def board(self, tag: str, value: float, step: int):
        if self.__board:
            self.__writer.add_scalar(tag, value, step)


class BaseFlowMeter:
    def __init__(self, logger: FlowLogger, max_len: int = 100) -> None:
        assert isinstance(logger, FlowLogger), "logger must be an instance of FlowLogger"
        self._start_time = datetime.now()
        self.logger: FlowLogger = logger
        self._episode_data_dict: Dict[str, List[float]] = defaultdict(lambda: [])
        self._epoch_data_dict: Dict[str, Deque[float]] = defaultdict(lambda: deque(maxlen=max_len))
        self._epoch_counter = 0

    @property
    def episode_return(self) -> float:
        if "returns" in self._episode_data_dict.keys():
            return np.mean(self._episode_data_dict["rewards/returns"])  # type: ignore
        else:
            return 0.0

    def init(self):
        self.logger._init_board()

    def store_episode_data(self, data_dict: Optional[Dict[str, List[Optional[float]]]]):
        """
        episode data is collected at the end of each episode from the envs
        """

        if data_dict is None:
            return
        for key, value in data_dict.items():
            self._episode_data_dict[key].extend([v for v in value if v is not None])

    def store_epoch_data(
        self, data_dict: Optional[Union[Dict[str, torch.Tensor], Dict[str, np.ndarray], Dict[str, float]]]
    ):
        """
        epoch data is collected at the end of each epoch from the algorithm
        """
        if data_dict is None:
            return
        for key, value in data_dict.items():
            if isinstance(value, torch.Tensor):
                self._epoch_data_dict[key].extend(value.cpu().flatten().tolist())
            elif isinstance(value, np.ndarray):
                self._epoch_data_dict[key].extend(value.flatten().tolist())
            elif isinstance(value, float) or isinstance(value, np.floating):
                self._epoch_data_dict[key].append(value)
            else:
                raise ValueError(f"value must be either torch.Tensor or np.ndarray, get type {type(value)}")

    def _store_data(
        self,
        target_dict: Dict[str, List[float]],
        data_dict: Optional[Dict[str, torch.Tensor]],
    ):
        if data_dict is None:
            return
        for key, value in data_dict.items():
            target_dict[key].extend(value.cpu().flatten().tolist())

    def _log_episode_data(
        self,
    ):
        for key, value in sorted(self._episode_data_dict.items()):
            if len(value) == 0:
                continue
            self.logger.info(
                f"{self._epoch_counter} - [{key}]: "
                f"mean:{np.mean(value):.4f}, "
                f"min:{np.min(value):.4f}, "
                f"max:{np.max(value):.4f}, "
                f"std:{np.std(value):.4f}",
            )
            self.logger.board(f"{key}[mean]", np.mean(value).astype(float), self._epoch_counter)
            # self.logger.board(f"{key}/min", np.min(value).astype(float), self._epoch_counter)
            # self.logger.board(f"{key}/max", np.max(value).astype(float), self._epoch_counter)
            # self.logger.board(f"{key}/std", np.std(value).astype(float), self._epoch_counter)

    def _log_epoch_data(self):
        for key, value in sorted(self._epoch_data_dict.items()):
            if len(value) == 0:
                continue
            self.logger.info(f"{self._epoch_counter} - [{key}]: " f"{value[-1]:.6f}, ")
            self.logger.board(f"{key}", value[-1], self._epoch_counter)

    def log(self):
        duration = datetime.now() - self._start_time
        self.logger.info(f"========== Epoch: {self._epoch_counter} - [Duration]: {duration} ==========")
        self._log_episode_data()
        self._log_epoch_data()
        self._epoch_counter += 1

    def reset(self):
        self._episode_data_dict: Dict[str, List[float]] = defaultdict(lambda: [])
        self._log_counter = 0


class VLogger:
    def __init__(
        self,
        log_type: LogType,
        log_path: Optional[os.PathLike],
    ) -> None:
        self.start_time_str = datetime.now(timezone.utc).astimezone().strftime("%d-%m-%y %H:%M:%S")
        self.log_type = log_type
        self.log_path = log_path
        self.__setup_logger_config()

    def __setup_logger_config(self):
        if self.log_type == LogType.File:
            assert self.log_path is not None, "log_path must be provided when log_type is File"
            loguru.add(self.log_path)

    def info_dict(self, dict_info: dict):
        if self.log_type == LogType.Vanish:
            return
        loguru.info(json.dumps(dict_info, sort_keys=False, indent=4))

    def info(self, msg: str):
        if self.log_type == LogType.Vanish:
            return
        loguru.info(msg)

    def debug(self, msg: str):
        if self.log_type == LogType.Vanish:
            return
        loguru.debug(msg)
