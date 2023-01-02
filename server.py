import socket
import threading
import queue
import constants


class User:
	def __init__(self, userSocket: socket, addr) -> None:
		self.userSocket = userSocket
		self.username = f"guest{len(users) + 1}"
		self.realname = ""
		self.addr = addr
		self.userThread = None


debug = True

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind(('', constants.serverPort))

serverSocket.listen()

users = {}

msgQueue = queue.Queue()

def acceptClient():
	while True:
		try:
			connectionSocket, addr = serverSocket.accept()
			if debug: print(f"Accepted connection from {addr}.")

			newUser = User(connectionSocket, addr)
			userThread = threading.Thread(target=handleUser, args=(newUser, ), daemon=True)
			newUser.userThread = userThread
			users[addr] = newUser
			newUser.userThread.start()

		except OSError:
			break

def handleUser(user: User):
	if debug: print(f"Handling user {user.username}.")
	while True:
		try:
			msgQueue.put((user.addr, user.userSocket.recv(constants.bufsize)))
		except:
			break


acceptThread = threading.Thread(target=acceptClient, daemon=True)
acceptThread.start()


while True:
	if msgQueue.empty(): continue

	msg = msgQueue.get()[1].decode()
	if msg == "exit":
		for user in users:
			user.userThread.close()
		
		serverSocket.close()
		break

	print(msg)