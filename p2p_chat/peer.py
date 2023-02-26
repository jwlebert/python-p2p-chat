from p2p_chat.connection import Connection
from p2p_chat.threads import ListenThread, InputThread
import socket
import threading

# TODO
# host -> addr

class Peer:
	def __init__(self, host='127.0.0.1', port=8080, name='user', key_input: bool = True):
		self.alive = True
		self.latest_request = None

		self.listen_thread = None # ? REQUIRED ???
		self.key_thread = None

		self.id = f'{host}:{port}:{name}'
		self.contacts = []

		self.commands = {
			'READ': self.read,
			'MEET': self.meet,
			'WELC': self.handle_welcome,
			'INTR': self.handle_introduction
		}

		self.listen_sock = self.create_socket(host, port)
		self.start_listen_thread()

		if key_input: self.start_key_thread()

	def create_socket(self, host, port, backlog=5):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind((host, port))
		s.listen(backlog)
		# creates a socket that will listen for connections from peers

		print("Socket created.")

		return s
	
	def start_listen_thread(self):
		self.listen_thread = ListenThread(func = self.await_peers)
	
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

	def handle_peer(self, conn_sock):
		host, port = conn_sock.getpeername()

		conn = Connection(host, port, conn_sock)

		command, data = conn.recvdata()
		print(command, data)
		self.handle_command(command.upper(), data)
		
		conn.close()

	def start_key_thread(self):
		"""Starts a KeyThread which will listen for input in the terminal."""
		self.key_thread = InputThread(callback = self.handle_keyboard_input,
				exit_func = self.close)

	def handle_keyboard_input(self, input_str): #TODO
		if input_str == 'l': print(self.contacts)
		try:
			a = input_str.split(';')
			host = a[0]
			port = int(a[1])
			msg = a[2]

			self.send_data(host, port, msg)
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
	
	def close(self) -> None:
		"""Performs all required actions to properly close a peer."""
		if self.key_thread is not None: self.key_thread.alive = False
		if self.listen_thread is not None: self.listen_thread.alive = False
		self.listen_sock.close()