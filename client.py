import socket as s
import sys
import signal



def handler(signum, _frame) :
    raise SystemExit(0)

signal.signal(signal.SIGINT, handler)

if len(sys.argv) != 3:
    print(f"usage: {sys.argv[0]} <USER>:<host> <port>")
    sys.exit(2)

try :
    port = int(sys.argv[2])
    user = str(sys.argv[1].split(':')[0])
    password = ""
except ValueError:
    print("[error]\tport must be an integer")
    sys.exit(2)

if not 1 <= port <= 65535:
    print("[error]\tport must be between 1 and 65535")
    sys.exit(2)

with s.socket(s.AF_INET, s.SOCK_STREAM) as client_s:
    try:
        client_s.connect((sys.argv[1].split(':')[1], port))
        print("[success]\tclient connected successfully")
        password = str(input("passwod : "))
    except OSError as exc:
        print(f"[error]\tconnect failed: {exc}")
        sys.exit(1)

    try:
        msg = client_s.recv(100)
        print(f"[server] : {msg.decode('utf-8', errors='replace')}")
    except OSError as exc:
        print(f"[error]\tclient can't receive message: {exc}")
        sys.exit(1)

    try:
        with client_s :
            message_send = f"CRE {user}:{password}\n".encode('utf-8')
            client_s.sendall(message_send)
            while True :
                string = str(input("$> "))
                if string.strip().lower() == "help":
                        print("""
                    ╔══════════════════════════════════════════════════════════════════╗
                    ║                     FTP CLIENT - HELP MENU                       ║
                    ╠══════════════════════════════════════════════════════════════════╣
                    ║                                                                  ║
                    ║  FILE OPERATIONS                                                 ║
                    ║  LIST                List files and directories                  ║
                    ║  RETR <filename>     Download a file from the server             ║
                    ║  STOR <filename>     Upload a file to the server                 ║
                    ║  DELE <filename>     Delete a file from the server               ║
                    ║  SIZE <filename>     Get the size of a file                      ║
                    ║                                                                  ║
                    ║  DIRECTORY OPERATIONS                                            ║
                    ║  PWD                 Show current remote directory               ║
                    ║  CWD <directory>     Change remote directory                     ║
                    ║  CDUP                Move to parent directory                    ║
                    ║  MKD <directory>     Create a remote directory                   ║
                    ║  RMD <directory>     Remove a remote directory                   ║
                    ║                                                                  ║
                    ║  CONNECTION                                                      ║
                    ║  NOOP                Check server connection                     ║
                    ║  SYST                Show server system type                     ║
                    ║  QUIT                Disconnect from FTP server                  ║
                    ║  HELP                Display this help menu                      ║
                    ╚══════════════════════════════════════════════════════════════════╝
                    """)
                else :
                    command = string.strip()
                    if command:
                        match command.split(maxsplit=1)[0].upper():

                            case (
                                "LIST"
                                | "PWD"
                                | "CWD"
                                | "CDUP"
                                | "MKD"
                                | "RMD"
                                | "DELE"
                                | "SIZE"
                                | "USER"
                                | "PASS"
                                | "RETR"
                                | "STOR"
                                | "SYST"
                                | "NOOP"
                                | "QUIT"
                            ):
                                client_s.sendall(
                                    f"{command}\r\n".encode("utf-8")
                                )

                                msg_s = client_s.recv(1024)

                                if not msg_s:
                                    print("[error]\t: Server disconnected")
                                    break

                                print(f"[server]\t\t: {msg_s.decode('utf-8')}",end="")

                                if command.split()[0].upper() == "QUIT":
                                    break

                            case _:
                                print(f"[error]\t\t: Unknown command: "
                                    f"{command.split()[0]}"
                                )


    except OSError as exc:
        print(f"[error]\tclient can't send message: {exc}")
        sys.exit(1)
