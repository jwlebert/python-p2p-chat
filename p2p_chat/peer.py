from p2p_chat.connection import Connection
from p2p_chat.keyboard import KeyboardThread
import socket
import threading

class Peer:
    def __init__(self, host='127.0.0.1', port=8080, name='user'):
        self.alive = True
        self.name = name
        self.contacts = []

        self.commands = {
            'READ': self.read,
        }

        self.listen_sock = self.create_socket(host, port)
        self.listen_sock.settimeout(1)
        # .accept() is blocking. the timeout ensures that other operations,
        # such as interrupts, can occur even if no connection is established
        
        self.key_thread = KeyboardThread(callback=self.handle_keyboard_input)

        while self.alive:
            self.await_peers()
        
        self.listen_sock.close()


    def create_socket(self, host, port, backlog=5):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(backlog)
        # creates a socket that will listen for connections from peers

        print("Socket created.")

        return s
    
    def await_peers(self):
        try:
            # print("Listening for connections... ")

            sock, addr = self.listen_sock.accept()
            print(addr)
            # listen for connections from peers
            sock.settimeout(None)

            t = threading.Thread(target = self.handle_peer, args = [sock])
            t.start()
            # create and start a thread to read what the connect said
        except KeyboardInterrupt:
            print("Keyboard Interrupt")
            self.alive = False
            # return
        except TimeoutError:
            pass
            # print("Timeout")
        except:
            print("error")

    def handle_peer(self, peer_sock):
        host, port = peer_sock.getpeername()
        # peer_id = {
        #     'host': host,
        #     'port': port
        # }
        # if peer_id not in self.peers: self.peers.append(peer_id)
        # print(self.peers)

        peer = Connection(host, port, peer_sock)

        command, data = peer.recvdata()
        print(command, data)
        print(self.handle_command(command.upper(), data))
        
        peer.close()

    def handle_keyboard_input(self, input_str):
        a = input_str.split(';')
        host = a[0]
        port = int(a[1])
        msg = a[2]


        # peer_id = self.peers[int(input_str[0])]
        # print(peer_id)
        # peer = Connection(peer_id['host'], peer_id['port'])
        peer = Connection(host, port)

        # peer.senddata(input_str[1:])
        peer.senddata(msg)
    
    def handle_command(self, command, arg):
        func = self.commands.get(command, None)
        if func is None:
            print("Command doesn't exist.")
            return

        try:
            if arg:
                func(arg)
            else:
                func()
        except:
            raise

        print("Success")
        return

    def read(self, data):
        print(data)