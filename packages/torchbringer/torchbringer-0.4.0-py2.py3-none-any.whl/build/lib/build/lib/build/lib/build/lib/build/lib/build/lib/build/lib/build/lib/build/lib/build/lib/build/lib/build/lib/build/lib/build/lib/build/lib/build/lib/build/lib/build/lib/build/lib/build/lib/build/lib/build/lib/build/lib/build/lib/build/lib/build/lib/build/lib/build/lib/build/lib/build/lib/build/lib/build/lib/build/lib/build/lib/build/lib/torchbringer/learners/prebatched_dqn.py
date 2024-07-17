import random

import torch

from torchbringer.components.replay_memory import ReplayMemory, Transition
import torchbringer.components.builders as builders
import torchbringer.learners.learner_utils as lu
from torchbringer.components.epsilon import Epsilon

# if GPU is to be used
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class PreBatchedDQN():
    """
    Deep Q Network - built based on https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html

    config spec
    {
        "action_space": action space spec (read builders.py) -> The environment's action space
        "gamma": float -> Value of gamma
        "tau": float = 1.0 -> Value of tau
        "target_network_update_frequency": int = 1 -> Steps before updating target network based on tau
        "epsilon": epsilon spec (read builders.py) -> Epsilon
        "batch_size": int -> Batch size
        "grad_clip_value": float -> Value to clip gradient. No clipping if not specified
        "loss": loss spec (read builders.py) -> Loss
        "optimizer": optimizer spec (read builders.py) -> Optimizer
        "replay_buffer_size": int -> capacity of the replay buffer
        "min_replay_size": int -> minimum size the replay must have for optimization to happen
        "network": List of layer specs (read builders.py) -> Sequential network that will be used
    }
    """

    def __init__(self, config):
        self.action_space = builders.build_space(config["action_space"])

        self.gamma = config["gamma"]
        self.tau = lu.value_or_default(config, "tau", 1.0)
        self.target_network_update_frequency = lu.value_or_default(config, "target_network_update_frequency", 1)
        self.epsilon: Epsilon = builders.build_epsilon(config["epsilon"])
        self.batch_size = config["batch_size"]
        self.grad_clip_value = lu.value_or_none(config, "grad_clip_value")
        self.min_replay_size = lu.value_or_default(config, "min_replay_size", 0)

        self.policy_net = builders.build_sequential(config["network"]).to(device)
        self.target_net = builders.build_sequential(config["network"]).to(device)
        self.target_net.load_state_dict(self.policy_net.state_dict())

        self.memory = ReplayMemory(config["replay_buffer_size"])
        self.loss = builders.build_loss(config["loss"])
        self.optimizer = builders.build_optimizer(self.policy_net, config["optimizer"])

        self.past_states = None
        self.past_actions = None

        self.steps_done = 0

        self.past_loss = 0.0


    def experience(self, states, rewards, terminals, infos):
        for i in range(self.batch_size):
            if not self.past_states[i] is None:
                self.memory.push(self.past_states[i], self.past_action, infos[i]["final_observation"] if terminals[i] else states[i], rewards[i])
        
        self.past_states = states
        self.past_states[terminals] = None

        
    def optimize(self):
        if len(self.memory) >= max(self.batch_size, self.min_replay_size):
            # Transpose batch
            transitions = self.memory.sample(self.batch_size)
            batch = Transition(*zip(*transitions))

            # Mask used to consider only non-terminal states
            non_final_mask = torch.tensor(tuple(map(lambda s: s is not None,
                                                batch.next_state)), device=device, dtype=torch.bool)
            
            non_final_next_states = [s for s in batch.next_state if s is not None]
            if len(non_final_next_states) == 0:
                non_final_next_states = None
            else:
                non_final_next_states = torch.cat([s for s in batch.next_state if s is not None])
            state_batch = torch.cat(batch.state)
            action_batch = torch.cat(batch.action)
            reward_batch = torch.cat(batch.reward)

            # Compute Q(s_t, a) for state action pairs in batch
            state_action_values = self.policy_net(state_batch).gather(1, action_batch)

            # Compute the expected Q values (r +  γ max_a ​Q(s′,a))
            next_state_values = torch.zeros(self.batch_size, device=device)
            if not non_final_next_states is None:
                with torch.no_grad():
                    next_state_values[non_final_mask] = self.target_net(non_final_next_states).max(1).values
            expected_state_action_values = (next_state_values * self.gamma) + reward_batch

            # Compute loss
            step_loss = self.loss(state_action_values, expected_state_action_values.unsqueeze(1))
            self.past_loss = step_loss.item()

            # Optimize the model
            self.optimizer.zero_grad()
            step_loss.backward()

            if not self.grad_clip_value is None:
                torch.nn.utils.clip_grad_value_(self.policy_net.parameters(), self.grad_clip_value)
            self.optimizer.step()
        
        self.steps_done += 1
        if self.steps_done % self.target_network_update_frequency == 0:
            # Soft update of the target network's weights
            # θ′ ← τ θ + (1 −τ )θ′
            target_net_state_dict = self.target_net.state_dict()
            policy_net_state_dict = self.policy_net.state_dict()
            for key in policy_net_state_dict:
                target_net_state_dict[key] = policy_net_state_dict[key]*self.tau + target_net_state_dict[key]*(1-self.tau)
            self.target_net.load_state_dict(target_net_state_dict)


    def select_action(self, states):
        samples = [random.random() for _ in range(self.batch_size)]
        eps_threshold = self.epsilon()
        self.past_actions = []
        for i in range(self.batch_size):
            if samples[i] > eps_threshold: # Action with largest Q value
                with torch.no_grad():
                    self.past_actions.append(self.policy_net(states[i]).max(1).indices.view(1, 1))
            else: # Random action
                self.past_actions.append(torch.tensor([[self.action_space.sample()]], device=device, dtype=torch.long))
        return self.past_actions