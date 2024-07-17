TorchBringer is an open-source framework that provides a simple interface for operating with pre-implemented deep reinforcement learning algorithms built on top of PyTorch. The interfaces provided can be used to operate deep RL agents either locally or remotely via gRPC. Currently, TorchBringer supports the following algorithms

- [x] DQN

## Quickstart

To install TorchBringer, run

```bash
pip install --upgrade pip
pip install torchbringer
```

### Local
Here's a simple project for running a TorchBringer agent on gymnasium's Cartpole environment.

```python
import gymnasium as gym
from itertools import count
import torch
from torchbringer.servers.torchbringer_agent import TorchBringerAgent

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

env = gym.make("CartPole-v1")
state, info = env.reset()

config = {
    # Check the reference section to understand config formatting
}

dqn = TorchBringerAgent()
dqn.initialize(config)
steps_done = 0

num_episodes = 600
for i_episode in range(num_episodes):
    state, info = env.reset()
    reward = torch.tensor([0.0], device=device)
    terminal = False
    
    state = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)
    for t in count():
        observation, reward, terminated, truncated, _ = env.step(dqn.step(state, reward, terminal).item())
        state = None if terminated else torch.tensor(observation, dtype=torch.float32, device=device).unsqueeze(0) 
        reward = torch.tensor([reward], device=device)
        terminal = terminated or truncated

        if terminal:
            dqn.step(state, reward, terminal)
            break
```

### Server
To start a TorchBringer server on a particular port, run

```bash
python -m torchbringer.servers.grpc.torchbringer_grpc_server <PORT> # For gRPC
python -m torchbringer.servers.socket.torchbringer_socket_server <PORT> # For socket
```

You can communicate with this server by using the provided Python client (see below) or develop a client of your own from the files found in `torchbringer/servers/grpc` in this repo to communicate with the server from applications built with different programming languages. 

```python
from torchbringer.servers.grpc.torchbringer_grpc_client import TorchBringerGRPCAgentClient
```

## Reference

`cartpole_local_dqn.py` provides a simple example of TorchBringer being used on gymnasium's CartPole-v1 envinronment. `cartpole_grpc_dqn.py` provides an example of how to use the gRPC interface to learn remotely.

The main class that is used in this framework is `TorchBringerAgent`, implemented in `servers/`. The gRPC server has an interface very similar to it.

### TorchBringerAgent
| Method | Parameters | Explanation |
|---|---|---|
| initialize() | config: dict | Initializes the agent according to the config. Read the config section for information on formatting |
| step() | state: Tensor, reward: Tensor, terminal: bool | Performs an optimization step and returns the selected action for this  |

### gRPC interface
Note that there is a client implemented in `servers/grpc/torchbringer_grpc_client.py` that has the exact same interface as `TorchBringerAgent`. This reference is mostly meant for building clients in other programming languages.

| Method | Parameters | Explanation |
|---|---|---|
| initialize() | config: string | Accepts a serialized config dict |
| step() | state: Matrix(dimensions list[int], value: list[float]), reward: float, terminal: bool | State should be given as a flattened matrix, action is returned the same way  |

### Socket interface
Note that there is a client implemented in `servers/socket/torchbringer_socket_client.py` that has the exact same interface as `TorchBringerAgent`. This reference is mostly meant for building clients in other programming languages.

Servers expect to receive a JSON string containing the field "method" for specifying the method by name as well as other parameters depending on the method. After being called, server will return a response in the form of another JSON string

| Method | Parameters | Explanation | Returns |
|---|---|---|---|
| "initialize" | config: JSON object | Accepts a serialized config dict | Information in the form {"info": string} |
| step() | state: list, reward: float, terminal: bool | The current percept from which to act | The action to take in the form {"action": list} |

## Config formatting
The config file is a dictionary that specifies the behavior of the agent. The RL implementation is specified by the value of the key "type". It also accepts a variety of other arguments depending on the imeplementation type.

Currently supported implementations are `dqn`.

The following specify the arguments allowed by each implementation type.

### DQN
| Argument | Explanation |
|---|---|
| "run_name": string | If given, will track episode reward and average loss through Aim for this run |
| "action_space": dict | The gym Space that represents the action space of the environment. Read the Space table on `Other specifications` |
| "gamma": float | Value of gamma |
| "tau": float = 1.0 | Value of tau |
| "target_network_update_frequency": int = 1 | Steps before updating target network based on tau |
| "epsilon": dict | The epsilon. Read the Epsilon table on `Other specifications` |
| "batch_size": int | Batch size |
| "grad_clip_value": float | Value to clip gradient. No clipping if not specified |
| "loss": dict | The loss. Read the Loss section on `Other specifications` |
| "optimizer": dict | The optimizer. Read the Optimizer section on `Other specifications` |
| "replay_buffer_size": int | Capacity of the replay buffer |
| "network": list[dict] | list of layer specs for the neural network. Read the Layers section on `Other specifications` |

### Other specifications

These are specifications for dictionaries that are used in the specification of learners. They each have an argument "type" and a corresponding class or function. In the case of classes, all of its initializing parameters can be passed as arguments in this dictionary. When specific arguments are expected, they will be made explicit.

#### Space
| Type | Class |
|---|---|
| discrete | `gym.spaces.Discrete` |

#### Epsilon
You can read `components/epsilon.py` to see how each of these are implemented
| Type | Arguments | Explanation
|---|---|---|
| exp_decrease | "start": float, "end": float, "steps_to_end": int | Decreases the epsilon exponentially over time.

#### Loss
| Type | Function |
|---|---|
| smooth_l1_loss | `torch.nn.SmoothL1Loss` |
| mseloss | `nn.MSELoss` |

#### Optimizer
| Type | Class |
|---|---|
| adamw | `torch.optim.AdamW` |
| rmsprop | `optim.RMSprop` |

#### Layers
| Type | Function |
|---|---|
| linear | `torch.nn.Linear` |
| relu | `torch.nn.ReLU` |

### Example config

``` python
config = {
    "type": "dqn",
    "action_space": {
        "type": "discrete",
        "n": 2
    },
    "gamma": 0.99,
    "tau": 0.005,
    "epsilon": {
        "type": "exp_decrease",
        "start": 0.9,
        "end": 0.05,
        "steps_to_end": 1000
    },
    "batch_size": 128,
    "grad_clip_value": 100,
    "loss": "smooth_l1_loss",
    "optimizer": {
        "type": "adamw",
        "lr": 1e-4, 
        "amsgrad": True
    },
    "replay_buffer_size": 10000,
    "network": [
        {
            "type": "linear",
            "in_features": int(n_observations),
            "out_features": 128,
        },
        {"type": "relu"},
        {
            "type": "linear",
            "in_features": 128,
            "out_features": 128,
        },
        {"type": "relu"},
        {
            "type": "linear",
            "in_features": 128,
            "out_features": int(n_actions),
        },
    ]
}
```