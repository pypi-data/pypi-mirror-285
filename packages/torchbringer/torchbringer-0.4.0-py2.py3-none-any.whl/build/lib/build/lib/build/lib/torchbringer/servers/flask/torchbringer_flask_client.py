import json
import numpy as np
import requests
import json

INITIALIZE = "/initialize"
STEP = "/step"

class TorchBringerFlaskAgentClient():
    def __init__(self, url="http://127.0.0.1:5000"):
        self.url = url
    

    def initialize(self, config):
        return json.loads(requests.post(self.url + INITIALIZE, json={"config": config}).text)


    def step(self, state, reward, terminal):
        return np.array(json.loads(requests.post(self.url + STEP, json={"state": [] if state is None else state.tolist(),
                                                                            "reward": reward,
                                                                            "terminal": terminal}).text)["action"])