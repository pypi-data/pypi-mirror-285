import os
import sys
parent = os.path.dirname(os.path.relpath("../"))
sys.path.append(parent)

import numpy as np
import grpc
import json

import torchbringer.servers.grpc.torchbringer_pb2 as pb2
import torchbringer.servers.grpc.torchbringer_pb2_grpc as pb2_grpc

class TorchBringerGRPCAgentClient():
    def __init__(self, port):
        self.channel = grpc.insecure_channel("localhost:" + str(port))
        self.stub = pb2_grpc.TorchBringerGRPCAgentStub(self.channel)
    

    def initialize(self, config):
        return self.stub.initialize(pb2.Config(serializedConfig=json.dumps(config))).info


    def step(self, state, reward, terminal):
        action = self.stub.step(pb2.Percept(
            state=pb2.Matrix(dimensions=[], values=[]) if state is None else pb2.Matrix(dimensions=state.shape, values=state.flatten()), 
            reward=reward, 
            terminal=terminal))
        return np.reshape(action.values, tuple(action.dimensions))