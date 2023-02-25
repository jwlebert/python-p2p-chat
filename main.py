from p2p_chat.peer import Peer

# host = input("host : ")
port = int(input("port : "))


peer = Peer(port=port)
peer.start_keythread()
while peer.alive:
    peer.await_peers()
    
# TODO LISTEN THREAD