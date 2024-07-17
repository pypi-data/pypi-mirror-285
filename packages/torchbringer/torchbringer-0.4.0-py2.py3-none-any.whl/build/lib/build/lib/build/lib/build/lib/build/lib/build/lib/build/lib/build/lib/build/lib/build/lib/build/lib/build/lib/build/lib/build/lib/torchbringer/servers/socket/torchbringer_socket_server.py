import sys
import socket
import json
import torch

from torchbringer.servers.torchbringer_agent import TorchBringerAgent


BUFSIZE = 9192

# if GPU is to be used
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def run_server(server_socket: socket.socket, port):
    """
    Accepts requests in the form of serialized jsons. Should be in the form

    {
        "method": "initialize" or "step"
        
        // For initialize
        "config": dict -> Config dictionary

        // For step
        "state": array -> Observation
        "reward": float -> Reward value
        "terminal": bool -> If is terminal
    }
    """
    server_socket.bind(("localhost", port))
    server_socket.listen(0)

    agent = TorchBringerAgent()
    while True:
        print(f"Listening on port {port}")
        conn, address = server_socket.accept()
        while True:
            data = conn.recv(BUFSIZE)
            if not data:
                break
            data_dict = json.loads(data)

            if try_correct_syntax(conn, data_dict, ["method"]): continue
            try:
                match data_dict["method"]:
                    case "initialize":
                        if try_correct_syntax(conn, data_dict, ["config"]): continue
                        agent.initialize(data_dict["config"])
                        send_json_to_client(conn, {"info": "Initialized agent"})
                    case "step":
                        if try_correct_syntax(conn, data_dict, ["state", "reward", "terminal"]): continue
                        send_json_to_client(conn, {"action": agent.step(
                            None if len(data_dict["state"]) == 0 else torch.tensor(data_dict["state"], device=device, dtype=torch.float32),
                            torch.tensor([data_dict["reward"]], device=device),
                            data_dict["terminal"]).tolist()})
                    case _:
                        send_json_to_client(conn, {"info": f"Unrecognized command f{data_dict['method']}"})
            except Exception as e:
                send_json_to_client(conn, {"info": f"Exception - {e}"})
        print("Client disconnected")



def send_json_to_client(conn, data_dict):
    conn.sendall(bytes(json.dumps(data_dict), encoding="utf-8"))

    
def try_correct_syntax(conn, data_dict, fields):
    """
    If any of the fields aren't present in data_dict, returns true and sends an error message. Otherwise, returns false
    """
    missing_fields = []
    for field in fields:
        if not field in data_dict: 
            missing_fields.append(field)
    
    if len(missing_fields) != 0:
        send_json_to_client(conn, {"info": f"Fields {', '.join(missing_fields)} missing from call"})
        return True
    return False


if __name__ == "__main__":
    if len(sys.argv) != 2 or not sys.argv[1].isdigit:
        print("Usage: torchbringer_socket_server.py <port>")
        exit()
    
    server_socket = socket.socket()
    try:
        run_server(server_socket, int(sys.argv[1]))
    except KeyboardInterrupt:
        print("Interrupted. Closing sockets...")
        server_socket.close()