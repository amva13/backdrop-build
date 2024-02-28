from syft.workers.websocket_server import WebsocketServerWorker
import syft as sy
import torch
hook = sy.TorchHook(torch)

kwargs = {
    "id": "bob",
    "host": "localhost",
    "port": 8778,
    "hook": hook,
    "verbose": True
}

if __name__ == "__main__":
    server = WebsocketServerWorker(**kwargs)
    print(server.start())
    print(server.list_objects())