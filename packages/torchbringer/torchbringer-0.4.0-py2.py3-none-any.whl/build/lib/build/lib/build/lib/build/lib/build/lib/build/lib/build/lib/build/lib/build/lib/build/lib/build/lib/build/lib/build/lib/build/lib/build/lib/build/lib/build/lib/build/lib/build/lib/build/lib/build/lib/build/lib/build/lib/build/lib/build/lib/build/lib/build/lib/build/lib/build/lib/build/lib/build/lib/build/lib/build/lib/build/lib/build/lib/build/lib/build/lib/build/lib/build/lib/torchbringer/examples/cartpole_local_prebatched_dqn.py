# Based on https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html

import gymnasium as gym
from itertools import count
from aim import Run

import torch

from torchbringer.servers.torchbringer_agent import TorchBringerAgent

# if GPU is to be used
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

env = gym.vector.make("CartPole-v1")
state, info = env.reset()
n_observations = len(state)

config = {
    "run_name": "Local Prebatched DQN CartPole",
    "type": "prebatched_dqn",
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
    "batch_size": 4,
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
            "in_features": 4,
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
            "out_features": 2,
        },
    ]
}
dqn = TorchBringerAgent()
dqn.initialize(config)


steps_done = 0

if torch.cuda.is_available():
    print("Running on GPU!")
    num_episodes = 600
else:
    print("Running on CPU!")
    num_episodes = 50

for i_episode in range(num_episodes):
    # Initialize the environment and get its state
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

print('Complete')