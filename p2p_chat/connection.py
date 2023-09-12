import socket
import struct
from typing import Tuple

class Connection:
	"""A connection between two peers.

	Used to transfer and receive data to and from peers.
	"""
	def __init__(self, addr: Tuple[str, int], sock: (socket.socket | None) = None) -> None:
		"""Initializes a socket connection listening to the specified address.

		Args:
			addr (str, int): a tuple of the target IPv4 address and port
			socket (socket): a socket objet; if there is already a
				socket for the connection, this will be used instead
				of a new one
		"""
		if sock is not None:
			self.sock = sock
		else:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.connect(addr)

		self.sock_data = self.sock.makefile('rwb', 0)
		# create a file object with that data from the socket
	
	def recvdata(self) -> tuple:
		"""Receives data sent from another peer.
		
		Returns:
			tuple: a tuple of the command and data received. Returns a
				tuple of (None, None) on error.
		"""
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
		
		self.close()

		return (command, data)
	
	def senddata(self, data: str) -> None:
		"""Sends data to a peer.

		Args:
			data (str): the first four characters should indicate the
				command, the rest is the data to be transfered.
		"""
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

		self.close()

	def close(self) -> None:
		"""Closes the socket connection."""
		self.sock.close()