import socket
import struct

class Connection:
    def __init__(self, host, port, sock=None):
        # TODO : maybe no listen sock
        # self.listen_server = listen_sock
        
        if sock is not None:
            self.sock = sock
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, int(port)))
        # define the socket connection, either by the socket object passed
        # or by the hostname and port

        # print(self.sock)

        self.sock_data = self.sock.makefile('rwb', 0)
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
    
    def senddata(self, data):
        command = data[:4].encode('utf-8')
        msg = data[4:].encode('utf-8')

        data = struct.pack("!4sI%ds" % len(msg), command, len(msg), msg)
        # "!4sL%ds" is the format that we are packing to
        # !     ->  bite order, size, alignment
        # 4s    ->  a string of 4 characters
        # I     ->  an unsigned int (4 byte number, with no sign (+/-))
        # %ds   ->  a string of length %d, where d is replaced by what follows
        #           the '%' after the format (in this case, len(msg))
        
        self.sock_data.write(data)

    def close(self):
        self.sock.close()
        self.sock = None