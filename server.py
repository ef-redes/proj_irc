import socket
import threading
import queue
import constants
from parse import *


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
			msgQueue.put((user.addr, user.userSocket.recv(constants.bufsize).decode()))
		except:
			break


acceptThread = threading.Thread(target=acceptClient, daemon=True)
acceptThread.start()

# TODO : Check if username and realname are well-formed.
def executeUser(addr, cmd: Command):
	users[addr].username = cmd.params["username"]
	users[addr].realname = cmd.params["realname"]

# TODO : Check if nick is well-formed.
def executeNick(addr, cmd: Command):
	users[addr].username = cmd.params["nickname"]

def executePrivmsg(addr, cmd: Command):
	target = cmd.params["target"]
	text = cmd.params["text"]

	if target[0] == "#":
		return

	for addrTarget in users:
		if users[addrTarget].username == target:
			msg = f"PRIVMSG {target} :{users[addr].username}: {text}"
			users[addrTarget].userSocket.send(msg.encode())

			return

	# TODO : Handle case where target was not found.
	
	



def handleMessage(msgPair) -> None:
	addr, msg = msgPair
	cmd = parseMessage(msg)

	if cmd.cmdType == CmdType.USER: executeUser(addr, cmd)
	elif cmd.cmdType == CmdType.NICK: executeNick(addr, cmd)
	elif cmd.cmdType == CmdType.PRIVMSG: executePrivmsg(addr, cmd)

while True:
	if msgQueue.empty(): continue

	handleMessage(msgQueue.get())