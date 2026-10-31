import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

with open(BASE_DIR / "config_server.json", "r") as file:
    config = json.load(file)

FTP_ROOT = (BASE_DIR / config["root_ftp_server"]).resolve()
FTP_ROOT.mkdir(parents=True, exist_ok=True)

HOST = config["host"]
PORT = config["port"]
MAX_CLIENTS = config["max_clients"]
BUFFER_SIZE = config["buffer_size"]