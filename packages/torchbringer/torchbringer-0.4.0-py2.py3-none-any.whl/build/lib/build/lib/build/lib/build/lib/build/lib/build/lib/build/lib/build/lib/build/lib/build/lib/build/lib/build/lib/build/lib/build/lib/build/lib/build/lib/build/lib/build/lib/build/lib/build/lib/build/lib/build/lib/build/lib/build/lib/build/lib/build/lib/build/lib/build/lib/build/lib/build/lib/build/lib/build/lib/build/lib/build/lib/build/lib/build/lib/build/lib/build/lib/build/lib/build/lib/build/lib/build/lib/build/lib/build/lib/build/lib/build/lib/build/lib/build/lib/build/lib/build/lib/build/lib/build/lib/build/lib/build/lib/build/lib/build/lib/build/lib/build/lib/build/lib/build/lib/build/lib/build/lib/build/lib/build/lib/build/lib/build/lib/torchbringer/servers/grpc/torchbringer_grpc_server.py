import os
import sys
parent = os.path.dirname(os.path.relpath("../"))
sys.path.append(parent)

import torch
import numpy as np
import grpc
import json
from concurrent import futures

from torchbringer.servers.torchbringer_agent import TorchBringerAgent

import torchbringer.servers.grpc.torchbringer_pb2 as pb2
import torchbringer.servers.grpc.torchbringer_pb2_grpc as pb2_grpc

# if GPU is to be used
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class TorchBringerGRPCAgentServicer(pb2_grpc.TorchBringerGRPCAgentServicer):
    def __init__(self):
        self.torch_deep_rl = None

    def initialize(self, request, context):
        self.torch_deep_rl = TorchBringerAgent()
        self.torch_deep_rl.initialize(json.loads(request.serializedConfig))
        return pb2.Confirmation(info="Initialized successfully")

    def step(self, request, context):
        if self.torch_deep_rl is None:
            return pb2.Matrix(dimensions=[], values=[])
        action = self.torch_deep_rl.step(
            None if len(request.state.dimensions) == 0 else torch.tensor(np.reshape(request.state.values, tuple(request.state.dimensions)), dtype=torch.float32, device=device), 
            torch.tensor([request.reward], device=device), 
            request.terminal)
        return pb2.Matrix(dimensions=action.shape, values=action.flatten())


def serve(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_TorchBringerGRPCAgentServicer_to_server(TorchBringerGRPCAgentServicer(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == "__main__":
    if len(sys.argv) != 2 or not sys.argv[1].isdigit:
        print("Usage: torch_deep_rl_grpc_server.py <port>")
        exit()
    
    serve(sys.argv[1])