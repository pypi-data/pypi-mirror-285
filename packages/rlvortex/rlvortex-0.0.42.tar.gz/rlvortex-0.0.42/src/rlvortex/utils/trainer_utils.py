import torch
import pdb
import torch.backends.mps
import numpy as np
import random

from typing import Union


def set_trace():
    pdb.set_trace()


def get_available_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def set_global_random_seed(rd_seed: int = 314):
    random.seed(rd_seed)
    np.random.seed(rd_seed)
    torch.manual_seed(rd_seed)
    torch.cuda.manual_seed(rd_seed)
    torch.cuda.manual_seed_all(rd_seed)
    torch.use_deterministic_algorithms(True)


"""
scale action from range [-1,1] to range [low,high]
"""


def scale_actions(actions: Union[np.ndarray, torch.Tensor], low, high):
    # if isinstance(low, np.ndarray):
    low = low.item()
    high = high.item()
    if isinstance(actions, np.ndarray):
        return np.clip((actions + 1) * (high - low) / 2 + low, low, high)
    elif isinstance(actions, torch.Tensor):
        return torch.clamp((actions + 1) * (high - low) / 2 + low, low, high)
    raise ValueError("Unsupported type of actions: {}".format(type(actions)))


"""
unscale action from range [low,high] to range [-1,1]
"""


def unscale_actions(actions: Union[np.ndarray, torch.Tensor], low, high):
    if isinstance(actions, np.ndarray):
        return np.clip((actions - low) * 2 / (high - low) - 1, -1, 1)
    elif isinstance(actions, torch.Tensor):
        return torch.clamp((actions - low) * 2 / (high - low) - 1, -1, 1)
    raise ValueError("Unsupported type of actions: {}".format(type(actions)))


def compute_discounted_returns(
    rewards: torch.Tensor, dones: torch.Tensor, last_values: torch.Tensor, gamma: float
) -> torch.Tensor:
    assert (
        rewards.shape == dones.shape
    ), f"rewards and dones must have the same shape but get {rewards.shape} and {dones.shape}"
    assert (
        last_values.dim() == 1
    ), f"last_values must be a 1-dim tensor but get {last_values.dim()}-dim tensor"
    num_transitions_per_env: int = rewards.shape[0]
    num_envs: int = rewards.shape[1]
    device: torch.device = rewards.device
    next_values: torch.Tensor = last_values
    returns: torch.Tensor = torch.zeros((num_transitions_per_env, num_envs), device=device)
    gamma = 1.0
    for step in reversed(range(num_transitions_per_env)):
        next_values = rewards[step] + gamma * (1 - dones[step]) * next_values
        returns[step] = next_values
    return returns


def compute_gae_returns(
    rewards: torch.Tensor,
    values: torch.Tensor,
    dones: torch.Tensor,
    last_values: torch.Tensor,
    gamma: float,
    lam: float,
) -> torch.Tensor:
    assert (
        rewards.shape == dones.shape and rewards.shape == values.shape
    ), f"rewards, values and dones must have the same shape but get {rewards.shape}, {values.shape} and {dones.shape}"
    assert (
        last_values.dim() == 1 and last_values.shape[0] == rewards.shape[1]
    ), f"last_values must be a 1-dim tensor but get {last_values.shape} shape"
    num_transitions_per_env: int = rewards.shape[0]
    num_envs: int = rewards.shape[1]
    device: torch.device = rewards.device
    next_values: torch.Tensor = last_values
    returns: torch.Tensor = torch.zeros((num_transitions_per_env, num_envs), device=device)
    gae: torch.Tensor = torch.zeros(num_envs, device=device)
    for step in reversed(range(num_transitions_per_env)):
        next_is_not_terminal = 1.0 - dones[step]
        delta = rewards[step] + next_is_not_terminal * gamma * next_values - values[step]
        gae = delta + next_is_not_terminal * gamma * lam * gae
        returns[step] = gae + values[step]
        next_values = values[step]
    return returns
