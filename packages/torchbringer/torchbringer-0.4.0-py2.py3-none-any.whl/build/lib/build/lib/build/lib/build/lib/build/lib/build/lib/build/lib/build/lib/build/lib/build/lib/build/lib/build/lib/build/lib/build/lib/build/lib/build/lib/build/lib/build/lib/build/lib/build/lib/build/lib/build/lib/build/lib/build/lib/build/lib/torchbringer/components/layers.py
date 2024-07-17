import torch.nn as nn
import torch


# if GPU is to be used
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class Normalize(nn.Module):
    def __init__(self, max):
        super(Normalize, self).__init__()
        self.max = torch.tensor(max, device=device)

    def forward(self, input):
        return input / self.max