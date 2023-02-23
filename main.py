from p2p_chat.peer import Peer

host = input("host : ")
port = int(input("port : "))


peer = Peer(host=host, port=port)