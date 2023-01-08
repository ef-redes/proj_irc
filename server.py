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
		self.channel : Channel = None

class Channel:
	def __init__(self, name : str, users: "set[User]") -> None:
		self.name = name
		self.users = users

debug = True

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind(('', constants.serverPort))

serverSocket.listen()

users = {}
channels = {}

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

def sendChannelMessage(origin : str, msg : str, name : str):
	msg = f"PRIVMSG {name} :{origin}: {msg}"
	for channelName in channels:
		if channelName == name:
			channel = channels[channelName]
			for user in channel.users:
				if user.username == origin: continue
				user.userSocket.send(msg.encode())
			return


def executePrivmsg(addr, cmd: Command):
	target = cmd.params["target"]
	text = cmd.params["text"]

	if target[0] == "#": sendChannelMessage(users[addr].username, text, target)

	for addrTarget in users:
		if users[addrTarget].username == target:
			msg = f"PRIVMSG {target} :{users[addr].username}: {text}"
			users[addrTarget].userSocket.send(msg.encode())

			return

	# TODO : Handle case where target was not found.

def joinChannel(user: User, channel : Channel):
	userChannel = user.channel
	if not userChannel == None:
		channels[userChannel.name].users.remove(user)

	user.channel = channel
	channel.users.add(user)

def executeJoin(addr, cmd : Command):
	channelExists = False
	for channelName in channels:
		channel = channels[channelName]
		if channel.name == cmd.params["channel"]:
			channel.users.add(users[addr])
			
			joinChannel(users[addr], channel)
			channelExists = True
			if debug: print(f"{users[addr].username} joined {channel.name}")
			break
	
	if not channelExists:
		if debug: print(f"Channel {cmd.params['channel']} created")
		channel = Channel(cmd.params["channel"], {users[addr]})
		channels[channel.name] = channel
		joinChannel(users[addr], channel)
		


def handleMessage(msgPair) -> None:
	addr, msg = msgPair
	cmd = parseMessage(msg)

	if cmd.cmdType == CmdType.USER: executeUser(addr, cmd)
	elif cmd.cmdType == CmdType.NICK: executeNick(addr, cmd)
	elif cmd.cmdType == CmdType.PRIVMSG: executePrivmsg(addr, cmd)
	elif cmd.cmdType == CmdType.JOIN: executeJoin(addr, cmd)

while True:
	if msgQueue.empty(): continue

	handleMessage(msgQueue.get())