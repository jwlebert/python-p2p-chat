from p2p_chat.connection import Connection
from p2p_chat.keyboard import KeyboardThread
import socket
import threading

# TODO
# host -> addr

class Peer:
	def __init__(self, host='127.0.0.1', port=8080, name='user'):
		self.alive = True
		self.id = f'{host}:{port}:{name}'
		self.contacts = []

		self.commands = {
			'READ': self.read,
			'MEET': self.meet,
			'WELC': self.handle_welcome,
			'INTR': self.handle_introduction
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
		self.handle_command(command.upper(), data)
		
		peer.close()

	def handle_keyboard_input(self, input_str):
		a = input_str.split(';')
		host = a[0]
		port = int(a[1])
		msg = a[2]

		self.send_data(host, port, msg)

		# peer_id = self.peers[int(input_str[0])]
		# print(peer_id)
		# # peer = Connection(peer_id['host'], peer_id['port'])
		# peer = Connection(host, port)

		# # peer.senddata(input_str[1:])
		# peer.senddata(msg)
	
	def handle_command(self, command: str, arg: str) -> None:
		"""Tries to execute a commands from other peers.

		Args:
			command (str): a four character string indicating the desired
				command.
			arg (str): arguments, typically the rest of the data received
				in a peer connection.
		"""
		func = self.commands.get(command, None)
		if func is None:
			raise Exception("Command doesn't exist.")

		try:
			if arg:
				func(arg)
			else:
				func()
		except:
			raise

		print("Success")
	
	def send_data(self, host: str, port: int, data: str) -> None:
		"""Sends data to the specified address.

		Args:
			host (str): IPv4 address of target.
			port (int): the target port.
			data (str): the data to be sent.
		"""
		peer = Connection(host, port)
		peer.senddata(data)
		peer.close() # ?

	def read(self, data):
		"""Prints received data to the console.

		Args:
			data (str): received data.
		"""
		print(data)
	
	def create_contact(self, contact_str):
		"""Creates and returns a dictionary objet based off of a contact id.

		Args:
			contact_str (str): the id of the contact, formatted as 
				'addr:port:name'

		Returns:
			dict: dictionary objet for the contact
		"""
		addr, port, name = contact_str.split(':')
		contact = {
			'id': f'{addr}:{port}:{name}', # same as contact_str
			'addr': addr,
			'port': int(port),
			'name': name
		}

		return contact

	def meet(self, contact_str):
		"""Handles a peer introducing itself to the network.

		The first contact from a peer to the peer network will be through this command.
		- introduces all other known contacts on the peer network
		- welcomes the new peer to the network
		- adds the contact information to the contacts

		Args:
			contact_str (str): formatted contact id of new peer.
		"""
		contact = self.create_contact(contact_str)

		if contact in self.contacts:
			print("Contact already exists")
			return
		
		self.introduce(contact)
		self.welcome(contact)
		self.contacts.append(contact)
	
	def introduce(self, new_contact):
		"""Introduces all existing peers in a network to a peer joining the network.

		Args:
			new_contact (str): the formatted contact id of the new peer to
				be introduced.
		"""
		for contact in self.contacts:
			peer = Connection(contact['addr'], contact['port'])
			peer.senddata('intr' + new_contact['id'])
	
	def handle_introduction(self, contact_str):
		"""Adds any introduced users to the contact list.

		Args:
			contact_str (str): formatted id of introduced contact.
		"""
		contact = self.create_contact(contact_str)
		self.contacts.append(contact)
	
	def welcome(self, contact):
		"""Introduces a peer joining a network to all known peers.
		
		Args:
			contact (dict): contact dict objet of new peer
		"""
		host, port = contact['addr'], int(contact['port'])
		peer = Connection(host, port)

		known_peers = [self.id]
		for contact in self.contacts:
			known_peers.append(contact['id'])
		
		data = 'welc' + ','.join(known_peers)
		peer.senddata(data)
	
	def handle_welcome(self, network_contacts):
		"""Stores all known peers of a network upon joining.
		
		Args:
			network_contacts (list): list of all the ids
				of contacts in the network
		"""
		new_contacts = network_contacts.split(',')
		for contact_str in new_contacts:
			contact = self.create_contact(contact_str)
			self.contacts.append(contact)        