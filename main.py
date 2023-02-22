import socket

HOST, PORT = '127.0.0.1', 8080

s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
s.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen( 5 )

sock, addr = s.accept()

print(sock, addr, sep = "\n")