import torchbringer.components.builders as builders
import torch

from aim import Run

# if GPU is to be used
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class TorchBringerAgent():
    def __init__(self) -> None:
        self.learner = None
    

    def initialize(self, config):
        self.run = None
        self.cummulative_loss = 0.0
        self.cummulative_reward = 0.0
        self.episode_steps = 0
        self.episode_counter = 1
        if "run_name" in config:
            self.run = Run(experiment=config["run_name"])
            self.run["hparams"] = config

        self.learner = builders.build_learner(config)
    

    def step(self, state, reward, terminal):
        self.learner.experience(state, reward, terminal)
        self.learner.optimize()

        if not self.run is None:
            self.cummulative_reward += reward
            self.cummulative_loss += self.get_past_loss()
            self.episode_steps += 1
            if terminal:
                self.run.track({"Episode reward": self.cummulative_reward, "Average loss": self.cummulative_loss / self.episode_steps}, step=self.episode_counter)
                self.cummulative_reward = 0.0
                self.cummulative_loss = 0.0
                self.episode_steps = 0
                self.episode_counter += 1

        return torch.tensor([], device=device) if state is None else self.learner.select_action(state)
    

    def get_past_loss(self):
        if hasattr(self.learner, "past_loss"):
            return self.learner.past_loss
        return 0.0