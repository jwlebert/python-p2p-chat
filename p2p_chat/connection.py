import socket
import struct

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

        self.sock_data = self.sock.makefile('rb', 0)
        # create a file object with that data from the socket
    
    def recvdata(self):
        try:
            command = self.sock_data.read(4).decode("utf-8")
            if not command: return (None, None)
            # check the type of message being sent (identifier)

            len_msg = self.sock_data.read(4)
            msg_len = struct.unpack("!I", len_msg)[0]
            if not msg_len: return (None, None)

            data = ""

            while len(data) != msg_len:
                d = self.sock_data.read(min(2048, msg_len - len(data)))
                # read either 2048 bytes or the remaining amount of data,
                # whichever is smaller
                if not len(d): break
                data += d.decode("utf-8")
            
            if len(data) != msg_len: return (None, None)
        except:
            return (None, None)
        
        return (command, data)
                    


    def close(self):
        self.sock.close()
        self.sock = None