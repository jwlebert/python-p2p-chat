import unittest

class TestPeerNetworking(unittest.TestCase):
	from p2p_chat.peer import Peer
	
	def test_meet(self):
		# Tests the meet command #
		addr1 = ('127.0.0.1', 12000)
		addr2 = ('127.0.0.1', 12001)

		# Initialize two peers on localhost
		peer1 = self.Peer(addr1, 'Peer1', key_input=False)
		peer2 = self.Peer(addr2, 'Peer2', key_input=False)

		# Peer1 sends a meet request to peer2
		peer1_id = f"{addr1[0]}:{str(addr1[1])}:Peer1"
		peer1.send_data(addr2, "MEET", peer1_id)

		# Wait until peer2 handles request
		while peer2.latest_request == None: pass

		# Check if the peer2 properly received contact
		peer1_contact = peer1.create_contact(peer1_id)
		self.assertIn(peer1_contact, peer2.contacts)

		# Close the peer servers
		peer1.close()
		peer2.close()

	def test_welcome(self):
		pass

	def test_introduce(self):
		pass

if __name__ == '__main__':
	unittest.main()