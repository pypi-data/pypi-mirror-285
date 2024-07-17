from flask import Flask
from flask import request
import json
import numpy as np
import torch
from torchbringer.servers.torchbringer_agent import TorchBringerAgent

MISSING_ARGS = "Missing args. Expected %s"

global agent

# if GPU is to be used
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

app = Flask(__name__)


@app.route("/initialize", methods=["POST"])
def initialize():
    if request.method == "POST":
        try:
            # Declares global vars
            global agent
            
            args = ["config"]
            data_dict = load_and_check_dict(request, args)
            if data_dict is None: return {"info": MISSING_ARGS % [", ".join(args)]}

            agent = TorchBringerAgent()
            agent.initialize(data_dict["config"])
            return {"info": "Agent initialized"}
        except Exception as e:
            return {"info": f"Exception - {e}"}


@app.route("/step", methods=["POST"])
def step():
    if request.method == "POST":
        try:
            # Declares global vars
            global agent

            args = ["state", "reward", "terminal"]
            data_dict = load_and_check_dict(request, args)
            if data_dict is None: return {"info": MISSING_ARGS % [", ".join(args)]}

            action = agent.step(None if len(data_dict["state"]) == 0 else torch.tensor(data_dict["state"], device=device, dtype=torch.float32),
                                            torch.tensor([data_dict["reward"]], device=device),
                                            data_dict["terminal"]).tolist()

            return {"action": action}
        except Exception as e:
            return {"info": f"Exception - {e}"}


def load_and_check_dict(request, fields):
    """
    Loads the dict from request. Returns the dict or None, in the case the dict doesn't include all fields present in fields
    """
    data_dict = json.loads(request.data)
    for field in fields:
        if not field in data_dict: 
            return None
    return data_dict
