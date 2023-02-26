from p2p_chat.peer import Peer

host = input("host : ")
port = int(input("port : "))

peer = Peer(port=port, key_input=True)

# THIS CODE WILL STILL EXECUTED (NOT-BLOCKED) #