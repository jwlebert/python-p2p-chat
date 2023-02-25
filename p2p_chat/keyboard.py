import threading

class KeyboardThread(threading.Thread):
	def __init__(self, callback = None, name = "keyboard-thread"):
		self.alive = True
		self.callback = callback
		super(KeyboardThread, self).__init__(name = name)
		self.start()

	def run(self):
		while self.alive:
			self.callback(input())