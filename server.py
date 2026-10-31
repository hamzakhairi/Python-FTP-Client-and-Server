import socket
import sys
import signal
import os
import subprocess
from pathlib import Path

FTP_ROOT = Path("./ftp_files").resolve()
FTP_ROOT.mkdir(exist_ok=True)


def send_response(client, message):
    client.sendall((message + "\r\n").encode("utf-8"))


def resolve_path(cwd, path):
    if path.startswith("/"):
        target = FTP_ROOT / path.lstrip("/")
    else:
        target = cwd / path

    target = target.resolve()

    if not target.is_relative_to(FTP_ROOT):
        raise PermissionError("Access outside FTP directory denied")

    return target


def handle_command(command, clientsocket, cwd):
    parts = command.strip().split(maxsplit=1)

    if not parts:
        send_response(clientsocket, "500 Empty command")
        return cwd

    cmd = parts[0].upper()
    arg = parts[1] if len(parts) > 1 else None
    print(f"g-{cmd}")
    try:
        match cmd:

            case "LIST":
                path = resolve_path(cwd, arg or ".")

                if not path.is_dir():
                    send_response(clientsocket, "550 Directory not found")
                    return cwd

                output = subprocess.run(
                    ["ls", "-la", "--", str(path)],
                    capture_output=True,
                    text=True,
                    check=True
                )

                send_response(clientsocket, output.stdout)

            case "PWD":
                print("[DEBUG] PWD matched!")
                relative = cwd.relative_to(FTP_ROOT)
                virtual_path = "/" if not relative.parts else "/" + relative.as_posix()

                send_response(clientsocket, f'257 "{virtual_path}"')

            case "CWD":
                if not arg:
                    send_response(clientsocket, "501 Missing directory")
                    return cwd

                path = resolve_path(cwd, arg)

                if not path.is_dir():
                    send_response(clientsocket, "550 Directory not found")
                    return cwd

                cwd = path
                send_response(clientsocket, "250 Directory changed")

            case "CDUP":
                cwd = resolve_path(cwd, "..")
                send_response(clientsocket, "250 Directory changed")

            case "RMD":
                if not arg:
                    send_response(clientsocket, "501 Missing directory")
                    return cwd

                path = resolve_path(cwd, arg)

                if path == FTP_ROOT:
                    raise PermissionError("Cannot remove FTP root")

                os.rmdir(path)
                send_response(clientsocket, "250 Directory removed")

            case _:
                send_response(clientsocket, "502 Command not implemented")

    except (OSError, ValueError, PermissionError) as error:
        send_response(clientsocket, f"550 Operation failed: {error}")

    return cwd

def handler(signum, _frame) :
    raise SystemExit(0)

signal.signal(signal.SIGINT, handler)

hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)

print(f'Hostname : {hostname}')
print(f'IP : {ip}')

if len(sys.argv) != 2:
    print(f"usage: {sys.argv[0]} <port>")
    sys.exit(2)

try:
    port = int(sys.argv[1])
except ValueError:
    print("[error]\t : port must be an integer")
    sys.exit(2)

if not 1 <= port <= 65535:
    print("[error]\t : port must be between 1 and 65535")
    sys.exit(2)

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('0.0.0.0', port))
        server_socket.listen(10)

        while True:
            try:
                clientsocket, address = server_socket.accept()
                print(f"[new]\t\t : new connection from {address[0]}:{address[1]}")
                clientsocket.sendall(b"Welcome to the server")
            except OSError as exc:
                print(f"[error]\t\t : accept failed: {exc}")
                continue

            with clientsocket:
                cwd = FTP_ROOT
                msg_c = bytearray()
                try:
                    while True:
                        msg = clientsocket.recv(1024)
                        if not msg:
                            if msg_c:
                                print(f"[client]\t : {msg_c.decode('utf-8', errors='replace')}", flush=True)
                                cwd = handle_command({msg_c.decode('utf-8', errors='replace')}, clientsocket, cwd)
                            break
                        msg_c.extend(msg)
                        while True:
                            newline_index = msg_c.find(b"\n")
                            if newline_index == -1:
                                break
                            line = msg_c[:newline_index].decode('utf-8', errors='replace').rstrip("\r")
                            del msg_c[:newline_index + 1]
                            print(f"[client]\t : {line}", flush=True)
                            cwd = handle_command(line, clientsocket, cwd)

                except OSError as exc:
                    print(f"[error]\t\t : client connection failed: {exc}")
except OSError as exc:
    print(f"[error]\t : server could not start: {exc}")
    sys.exit(1)
