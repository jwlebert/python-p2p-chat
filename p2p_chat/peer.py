import socket
import threading
from typing import Tuple

from p2p_chat.connection import Connection
from p2p_chat.threads import ListenThread, InputThread

class Peer:
	def __init__(self, addr: Tuple[str, int] = ('127.0.0.1', 8080), name: str = 'user', key_input: bool = False) -> None:
		"""Initializes a peer and listens for connections.

		Args:
			addr (str, int): the peer's address, comprised of it's IPv4 address
				and port.
			name (str): the peer's name.
			key_input (bool): if the peer will listen for input on a thread.
		"""
		self.alive = True
		self.latest_request = None

		self.listen_thread = None # ? REQUIRED ???
		self.key_thread = None

		host, port = addr
		self.id = f'{host}:{port}:{name}'
		self.contacts = []

		self.commands = {
			'READ': self.read,
			'MEET': self.meet,
			'WELC': self.handle_welcome,
			'INTR': self.handle_introduction
		}

		self.listen_sock = self.create_socket(addr)
		self.start_listen_thread()

		if key_input: self.start_key_thread()

	def create_socket(self, addr: Tuple[str, int], backlog: int = 5) -> socket.socket:
		"""Creates a listening socket at the specified address.

		Args:
			addr (str, int): the address to listen to (IPv4, port)
			backlog (int): how many requests can be queued before blocking
				new requests

		Returns:
			socket: a socket created based off the parameters
		"""
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind(addr)
		s.listen(backlog)

		print("Socket created.")

		return s
	
	def start_listen_thread(self) -> None:
		"""Start a thread to listen for connections from peers."""
		self.listen_thread = ListenThread(func = self.await_peers)
	
	def await_peers(self) -> None:
		"""Listens for and handles requests from peers."""
		try:
			print("Listening for connections... ")

			sock, addr = self.listen_sock.accept()
			sock.settimeout(None)

			t = threading.Thread(target = self.handle_peer, args = [sock])
			t.start()
			# create and start a thread to read what the connect said
		except KeyboardInterrupt:
			print("Keyboard Interrupt")
			self.close()
			# return
		except TimeoutError:
			pass
		except OSError as e:
			if (e.errno == 10038 and not self.listen_thread.alive):
			# this error is raised when the peers close, because the listen_thread
			# is still trying to accept a request, but the sockets closed, so they
			# are no longer considered sockets. 
				return
			else: 
				print(e)
				raise
		except:
			raise

	def handle_peer(self, conn_sock: socket.socket) -> None:
		"""Handles a connection from a peer.

		Args:
			conn_sock (socket): the socket created from the peer's
				connection
		"""
		addr = conn_sock.getpeername()

		conn = Connection(addr, conn_sock)

		command, data = conn.recvdata()
		print(command, data)
		self.handle_command(command.upper(), data)
		
		conn.close()

	def start_key_thread(self) -> None:
		"""Starts a KeyThread which will listen for input in the terminal."""
		self.key_thread = InputThread(callback = self.handle_keyboard_input,
				exit_func = self.close)

	def handle_keyboard_input(self, input_str: str) -> None:
		"""Handles keyboard input from the peers InputThread.

		Args:
			input_str (str): string of the input from the console
		"""
		if input_str == 'l': print(self.contacts) # DEBUG TODO
		try:
			fields = input_str.split(';')
			
			host = fields[0]
			port = int(fields[1])
			addr = (host, port)

			msg = fields[2]
			command = msg[:4]
			data = msg[4:]

			self.send_data(addr, command, data)
		except:
			raise Exception("Invalid input.")
	
	def handle_command(self, command: str, arg: str) -> None:
		"""Tries to execute a commands from other peers.

		Args:
			command (str): a four character string indicating the desired
				command.
			arg (str): arguments, typically the rest of the data received
				in a peer connection.
		"""
		command = command.upper()
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

		self.latest_request = (command, arg)
	
	def send_data(self, addr: Tuple[str, int], command: str, data: str) -> None:
		"""Sends data to the specified address.

		Args:
			addr (str, int): a tuple of the IPv4 address of the target
				and the target port.
			command (str): the command to indicate how to handle the data
				(see peer.commands)
			data (str): the data to be sent.
		"""
		formatted_data = f"{command.upper()}{data}"
		peer = Connection(addr)
		peer.senddata(formatted_data)
		peer.close() # ?

	def read(self, data):
		"""Prints received data to the console.

		Args:
			data (str): received data.
		"""
		print(data)
	
	def create_contact(self, contact_id):
		"""Creates and returns a dictionary objet based off of a contact id.

		Args:
			contact_str (str): the id of the contact, formatted as 
				'addr:port:name'

		Returns:
			dict: dictionary objet for the contact
		"""
		host, port, name = contact_id.split(':')
		contact = {
			'id': f'{host}:{port}:{name}', # same as contact_str
			'addr': (host, int(port)),
			'host': host,
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
			peer = Connection(contact['addr'])
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
		peer = Connection(contact['addr'])

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
	
	def close(self) -> None:
		"""Performs all required actions to properly close a peer."""
		if self.key_thread is not None: self.key_thread.alive = False
		if self.listen_thread is not None: self.listen_thread.alive = False
		self.listen_sock.close()