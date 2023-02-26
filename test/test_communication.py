import unittest

class TestCommunication(unittest.TestCase):

	from p2p_chat.peer import Peer
    
	def test_read(self):
		# Tests basic send/receive functionality. #

		# Initialize two peers on the localhost
		peer1 = self.Peer('127.0.0.1', 12001, key_input=False)
		peer2 = self.Peer('127.0.0.1', 12002, key_input=False)

		### Check sending peer1 -> peer2
		peer1.send_data('127.0.0.1', 12002, "readHello, world!")

		while peer2.latest_request == None: pass # wait for data

		command, data = peer2.latest_request
		peer2.latest_request = None # clear

		self.assertEqual(command, 'READ')
		self.assertEqual(data, "Hello, world!")

		### Check sending peer2 -> peer1
		peer2.send_data('127.0.0.1', 12001, "readNice to meet you.")

		while peer1.latest_request == None: pass # wait for data
		
		command, data = peer1.latest_request
		peer1.latest_request = None # clear

		self.assertEqual(command, 'READ')
		self.assertEqual(data, "Nice to meet you.")

		peer1.close()
		peer2.close()

	# TODO test_networking

if __name__ == '__main__':
	unittest.main()