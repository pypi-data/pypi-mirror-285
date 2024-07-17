import socket
import json
import numpy as np


BUFSIZE = 4096


class TorchBringerSocketAgentClient():
    def __init__(self, port):
        self.client_socket = socket.socket()
        self.client_socket.connect((socket.gethostname(), port))
    

    def initialize(self, config):
        if self.client_socket is None: return

        self.send_json_to_server({"method": "initialize", "config": config})
        return self.receive_json_from_server()


    def step(self, state, reward, terminal):
        if self.client_socket is None: return

        self.send_json_to_server({
            "method": "step",
            "state": state.tolist(),
            "reward": reward,
            "terminal": terminal
        })
        return np.array(self.receive_json_from_server()["action"])


    def send_json_to_server(self, data_dict):
        self.client_socket.sendall(bytes(json.dumps(data_dict), encoding="utf-8"))
    

    def receive_json_from_server(self):
        return json.loads(self.client_socket.recv(BUFSIZE))
    

    def close(self):
        self.client_socket.close()
        self.client_socket = None