from typing import Callable, Union
import torch
import torch.nn as nn
import numpy as np


def mlp(
    sizes,
    activation,
    output_activation: Callable = nn.Identity,
    last_scale: Union[float, np.floating] = 1.0,
    default_init: bool = True,
):
    layers = []
    for j in range(len(sizes) - 1):
        act = activation if j < len(sizes) - 2 else output_activation
        layers += [nn.Linear(sizes[j], sizes[j + 1]), act()]
    module = nn.Sequential(*layers)
    weights = [np.sqrt(2)] * (len(sizes) - 2) + [last_scale]
    if default_init:
        init_weights(module, weights)
    return module


def init_weights(sequential, weights):
    [
        torch.nn.init.orthogonal_(module.weight, gain=weights[idx])
        for idx, module in enumerate(mod for mod in sequential if isinstance(mod, nn.Linear))
    ]
