# Python-FTP-Client-and-Server
A simple FTP client and server built with Python sockets to transfer files over a network.

# Python FTP Server

A simple FTP client and server built with Python sockets to transfer files over a network.

## Features

| Command | Description | Status |
|---------|-------------|--------|
| LIST | List directory contents | Done |
| PWD | Show current directory | Done |
| CWD | Change directory | Done |
| CDUP | Go to parent directory | Done |
| RMD | Remove directory | Done |
| MKD | Create directory | TODO |
| DELE | Delete file | TODO |
| SIZE | Get file size | TODO |
| USER | Send username | TODO |
| PASS | Send password | TODO |
| RETR | Download file | TODO |
| STOR | Upload file | TODO |
| SYST | Get server system | TODO |
| NOOP | Check connection | TODO |
| QUIT | Disconnect | TODO |

## Usage

Start the server:

```bash
python3 server.py 2121
```

Connect with the client:

```bash
python3 client.py username:localhost port
```

## Notes

- Built using Python's `socket` module.
- Files are managed inside the `ftp_files` directory.
- File upload and download are not implemented yet.
- This is a learning project, not a complete FTP implementation.