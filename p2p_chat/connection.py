import socket

class Connection:
    def __init__(self, listen_sock, host, port, sock=None):
        # TODO : maybe no listen sock
        self.listen_server = listen_sock
        
        if sock is not None:
            self.sock = sock
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, int(port)))
        # define the socket connection, either by the socket object passed
        # or by the hostname and port

    def close(self):
        self.sock.close()
        self.sock = None