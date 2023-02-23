from p2p_chat.connection import Connection
import sys, os, traceback
import socket
import threading

class Peer:
    def __init__(self, host='127.0.0.1', port=8080):
        self.alive = True
        self.peers = []

        self.listen_sock = self.create_socket(host, port)
        self.listen_sock.settimeout(2)
        # .accept() is blocking. the timeout ensures that other operations,
        # such as interrupts, can occur even if no connection is established

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
            print("Listening for connections... ")

            sock, addr = self.listen_sock.accept()
            # listen for connections from peers
            print(sock)
            sock.settimeout(None)

            t = threading.Thread(target = self.handle_peer, args = [sock])
            t.start()
            # create and start a thread to read what the connect said
        except KeyboardInterrupt:
            print("Keyboard Interrupt")
            self.alive = False
            # return
        except TimeoutError:
            print("Timeout")
        except:
            print("error")

    def handle_peer(self, peer_sock):
        host, port = peer_sock.getpeername()
        print(host, port)
        peer = Connection(self, host, port, peer_sock)
        self.peers.append(peer)

        peer.loop()
        
        self.peers.remove(peer) # potential source of error
        peer.close()