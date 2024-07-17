import gymnasium as gym
import torch.optim as optim
import torch.nn as nn
import torch.nn.functional as F

from torchbringer.components import epsilon
from torchbringer.learners.dqn import DQN
import torchbringer.components.layers as tb_layers
LEARNER_STRING_TO_CLASS = {
    "dqn": DQN
}
SPACE_STRING_TO_CLASS = {
    "discrete": gym.spaces.Discrete
}
EPSILON_STRING_TO_FUNC = {
    "exp_decrease": epsilon.exp_decrease,
    "lin_decrease": epsilon.lin_decrease
}
LAYER_STRING_TO_CLASS = {
    "linear": nn.Linear,
    "relu": nn.ReLU,
    "conv2d": nn.Conv2d,
    "maxpool2d": nn.MaxPool2d,
    "flatten": nn.Flatten,
    "normalize": tb_layers.Normalize
}
LOSS_STRING_TO_FUNC = {
    "smooth_l1_loss": nn.SmoothL1Loss(),
    "mseloss": nn.MSELoss()
}
OPTIMIZER_STRING_TO_CLASS = {
    "adamw": optim.AdamW,
    "rmsprop": optim.RMSprop
}

def build_learner(config):
    """
    Receives a config dictionary that specifies a deep RL module. The specific parameters required depend on the
    module type
    """
    return LEARNER_STRING_TO_CLASS[config["type"]](build_kwargs(config))



def build_space(config) -> gym.Space:
    """
    Receives a config dictionary that specifies an action space. The specific parameters required depend on the
    space type

    If given a space, will simply return it
    """
    if isinstance(config, gym.Space):
        return config
    return SPACE_STRING_TO_CLASS[config["type"]](**build_kwargs(config))




def build_epsilon(config) -> epsilon.Epsilon:
    """
    Receives a config dictionary that specifies the type and parameters of epsilon. The specific parameters
    required depend on the epsilon type
    """
    return epsilon.Epsilon(EPSILON_STRING_TO_FUNC[config["type"]], **build_kwargs(config))


def build_sequential(config) -> nn.Sequential:
    """
    Receives a config array such that each of its elements is a dictionary that specifies a layer of the NN. While
    each layer has the attribute "type", other required attributes depend on the type of layer
    """
    layers = []

    for layer_spec in config:
        layers.append(LAYER_STRING_TO_CLASS[layer_spec["type"]](**build_kwargs(layer_spec)))
    
    return nn.Sequential(*layers)


def build_loss(type) -> callable:
    """
    Returns a loss function given its name
    """
    return LOSS_STRING_TO_FUNC[type]


def build_optimizer(module: nn.Module, config) -> optim.Optimizer:
    """
    Receives a config dictionary that specifies the type and parameters of optimizer. The specific parameters
    required depend on the optimizer type
    """
    return OPTIMIZER_STRING_TO_CLASS[config["type"]](module.parameters(), **build_kwargs(config))


def build_kwargs(config):
    """
    Should look for any necessary substitutions to specific objects or formats before building kwargs
    """
    return build_excluding_dict(config, ["type"])


def build_excluding_dict(dict, excludes):
    kwargs = {}
    for k in dict:
        if not k in excludes:
            kwargs[k] = dict[k]
    return kwargs