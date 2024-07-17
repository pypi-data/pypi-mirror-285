# Based on Mnih, Volodymyr, et al. "Playing atari with deep reinforcement learning." arXiv preprint arXiv:1312.5602 (2013).

import datetime
import time
import gymnasium as gym
from itertools import count
from aim import Run

import torch
import cv2
import numpy as np

from torchbringer.servers.torchbringer_agent import TorchBringerAgent

class AtariEnv():
    def __init__(self, name, stacked_frames, frames_clipped):
        self.env = gym.make(name)

        self.past_frames = []
        self.stacked_frames = stacked_frames
        self.frames_clipped = frames_clipped
    

    def preprocess_state(self, state, past_state=None):
        grayscale_state = np.array(cv2.resize(cv2.cvtColor(state, cv2.COLOR_RGB2GRAY), (110, 84))[:, 13:97], dtype=np.uint8)
        if past_state is None:
            return grayscale_state
        return cv2.max(grayscale_state, past_state)


    def get_current_state(self):
        return np.array(self.past_frames)


    def step(self, action):
        total_reward = 0.0
        for i in range(self.frames_clipped):
            observation, reward, terminated, truncated, info = self.env.step(action)

            if reward > 0:
                reward = 1.0
            if reward < 0:
                reward = -1.0
            total_reward += reward

            if terminated or truncated:
                break

        self.past_frames[:self.stacked_frames-1, :, :] = self.past_frames[1:self.stacked_frames, :, :]
        self.past_frames[self.stacked_frames-1, :, :] = self.preprocess_state(observation, self.past_frames[-2])

        return self.get_current_state(), total_reward, terminated, truncated, info


    def reset(self):
        state, info = self.env.reset()
        self.past_frames = np.zeros((self.stacked_frames, 84, 84), dtype=np.uint8)
        self.past_frames[self.stacked_frames-1, :, :] = self.preprocess_state(state)

        return self.get_current_state(), info

# if GPU is to be used
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

env = AtariEnv("ALE/Breakout-v5", 4, 4)
state, info = env.reset()

config = {
    "type": "dqn",
    "run_name": "DQN Breakout",
    "action_space": {
        "type": "discrete",
        "n": 4
    },
    "gamma": 0.99,
    "target_network_update_frequency": 10000,
    "epsilon": {
        "type": "lin_decrease",
        "start": 1.0,
        "end": 0.1,
        "steps_to_end": 1000000
    },
    "batch_size": 32,
    "grad_clip_value": 1,
    "loss": "mseloss",
    "optimizer": {
        "type": "rmsprop",
        "lr": 0.00025, 
        "momentum": 0.95
    },
    "replay_buffer_size": 1000000,
    "min_replay_size": 50000,
    "network": [
        {
            "type": "normalize",
            "max": 255.0
        },
        {
            "type": "conv2d",
            "in_channels": 4,
            "out_channels": 32,
            "kernel_size": 8,
            "stride": 4
        },
        {"type": "relu"},
        {
            "type": "conv2d",
            "in_channels": 32,
            "out_channels": 64,
            "kernel_size": 4,
            "stride": 2
        },
        {"type": "relu"},
        {
            "type": "conv2d",
            "in_channels": 64,
            "out_channels": 64,
            "kernel_size": 3,
            "stride": 1
        },
        {"type": "relu"},
        {"type": "flatten"},
        {
            "type": "linear",
            "in_features": 3136, 
            "out_features": 512
        },
        {"type": "relu"},
        {
            "type": "linear",
            "in_features": 512,
            "out_features": 4,
        }
    ]
}

dqn = TorchBringerAgent()
dqn.initialize(config)

frames_done = 0
log_interval = 10000
if torch.cuda.is_available():
    print("Running on GPU!")
    total_frames = 10000000
else:
    print("Running on CPU!")
    total_frames = 1000

starting_time = time.time()
last_log_time = time.time()
for i_episode in count():
    # Initialize the environment and get its state
    state, info = env.reset()
    reward = torch.tensor([0.0], device=device)
    terminal = False

    cummulative_reward = 0.0
    cummulative_loss = 0.0
    first_episode_frame = frames_done
    
    state = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)
    for t in count():
        observation, reward, terminated, truncated, _ = env.step(dqn.step(state, reward, terminal).item())
        cummulative_reward += reward
        cummulative_loss += dqn.get_past_loss()

        state = None if terminated else torch.tensor(observation, dtype=torch.uint8, device=device).unsqueeze(0) 
        reward = torch.tensor([reward], device=device)
        terminal = terminated or truncated

        frames_done += 1
        if frames_done % log_interval == 0:
            current_time = time.time()
            print("Finished %d/%d frames in %s - ETR: %ss; TE: %ss" % (frames_done, total_frames, datetime.timedelta(seconds=int(current_time - last_log_time)), datetime.timedelta(seconds=int((current_time - starting_time) / frames_done * (total_frames - frames_done))), datetime.timedelta(seconds=int(current_time - starting_time))))
            last_log_time = current_time

        if terminal:
            dqn.step(state, reward, terminal)
            break

    if frames_done >= total_frames:
        break

print("Complete in %.2fs" % (time.time() - starting_time))