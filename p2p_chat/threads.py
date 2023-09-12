import threading

class ListenThread(threading.Thread):
	"""Loops the specified function."""
	def __init__(self, func: callable = None, name: str = "listen-thread"):
		"""Initializes a thread that loops a specfied function.
		
		Args:
			func (callable): the function to be looped.
			name (str): the name of the thread.
		"""
		self.alive = True
		self.func = func
		super(ListenThread, self).__init__(name = name)
		self.start()
	
	def run(self) -> None:
		"""Loops while the thread is active."""
		while self.alive:
			try:
				self.func()
			except OSError as e:
				if (e.errno == 10038 and not self.alive):
				# this error is raised when the peers close, because the listen_thread
				# is still trying to accept a request, but the sockets closed, so they
				# are no longer considered sockets. 
					return
				else: 
					raise
			

class InputThread(threading.Thread):
	"""Awaits input, then passes it to the callback function upon submission."""
	def __init__(self, callback: callable = None, exit_func: callable = None, name = "input-thread"):
		"""Initializes a thread to handle user input.

		Args:
			callback (callable): the function to be called upon input submission.
				user input is passed as an argument.
			exit_func (callable): an exit function to be called when a
				KeyboardInterupt exception is raised.
			name (str): the name of the thread.
		"""
		self.alive = True
		self.callback = callback
		self.exit_func = exit_func
		super(InputThread, self).__init__(name = name)
		self.start()

	def run(self) -> None:
		"""Loops while the thread is active."""
		while self.alive:	
			try:
				self.callback(input())
			except KeyboardInterrupt:
				self.exit_func()
			except EOFError: # caused by thread shutting down without any input ?
				self.exit_func()
			except Exception as e:
				if e.args[0] != "Invalid input.": raise