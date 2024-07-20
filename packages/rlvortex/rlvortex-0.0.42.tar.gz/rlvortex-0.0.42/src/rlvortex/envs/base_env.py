import abc
from typing import Any, Dict, Optional, Tuple

import torch


class BaseEnvTrait(abc.ABC):
    def __init__(self, num_envs: int = 1) -> None:
        super().__init__()
        assert isinstance(num_envs, int) and num_envs > 0, "num_envs must be a positive integer"
        self.num_envs = num_envs

    @property
    @abc.abstractmethod
    def params(self) -> Dict[str, Any]:
        return {
            "num_envs": self.num_envs,
        }

    @property
    @abc.abstractmethod
    def renderable(self):
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def observation_dim(self):
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def action_dim(self):
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def action_n(self):
        raise NotImplementedError

    @abc.abstractmethod
    def awake(self):
        raise NotImplementedError

    @abc.abstractmethod
    def reset(self, reset_indices: Optional[Any] = None) -> Tuple[torch.Tensor, Dict]:
        raise NotImplementedError

    @abc.abstractmethod
    def step(self, action) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, Dict]:
        raise NotImplementedError

    @abc.abstractmethod
    def sample_action(self):
        raise NotImplementedError

    @abc.abstractmethod
    def render(self):
        raise NotImplementedError

    @abc.abstractmethod
    def destory(self):
        raise NotImplementedError


class EnvWrapper(BaseEnvTrait):
    def __init__(self, *, env: BaseEnvTrait) -> None:
        self.env: BaseEnvTrait = env
        self.__awaked = False
        self.__reseted = False
        self.__destoryed = False

    @property
    def params(self) -> Dict[str, Any]:
        return self.env.params

    @property
    def num_envs(self):
        return self.env.num_envs

    @property
    def renderable(self):
        return self.env.renderable

    @property
    def observation_dim(self):
        return self.env.observation_dim

    @property
    def action_dim(self):
        return self.env.action_dim

    @property
    def action_n(self):
        return self.env.action_n

    def awake(
        self,
    ):
        assert not self.__destoryed, "env must not be destoryed before awake"
        self.__awaked = True
        self.env.awake()
        return self

    def reset(self, reset_indices: Optional[Any] = None):
        assert not self.__destoryed, "env must not be destoryed before awake"
        assert self.__awaked, "env must be awaked before reset"
        self.__reseted = True
        return self.env.reset(reset_indices)

    def step(self, actions) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, Dict]:
        assert not self.__destoryed, "env must not be destoryed before awake"
        assert self.__awaked, "env must be awaked before step"
        assert self.__reseted, "env must be reseted before step"
        return self.env.step(actions)

    def sample_action(self):
        return self.env.sample_action()

    def render(self):
        assert not self.__destoryed, "env must not be destoryed before awake"
        assert self.__awaked, "env must be awaked before render"
        assert self.__reseted, "env must be reseted before render"
        self.env.render()

    def destory(self):
        self.__destoryed = True
        return self.env.destory()
