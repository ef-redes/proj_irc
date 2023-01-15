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

def executeUser(addr, cmd: Command):
	users[addr].username = cmd.params["username"]
	users[addr].realname = cmd.params["realname"]

def executeNick(addr, cmd: Command):
	users[addr].username = cmd.params["nickname"]

def sendChannelMessage(origin : str, msg : str, name : str, raw=False):
	if not raw: msg = f"PRIVMSG {name} :{origin}: {msg}"
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

def joinChannel(user: User, channel : Channel):
	removeFromChannel(user)

	user.channel = channel
	channel.users.add(user)

def executeJoin(addr, cmd : Command):
	if users[addr].channel != None and users[addr].channel.name == cmd.params['channel']: return

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
		if cmd.params["channel"][0] != "#": return
		if debug: print(f"Channel {cmd.params['channel']} created")
		channel = Channel(cmd.params["channel"], {users[addr]})
		channels[channel.name] = channel
		joinChannel(users[addr], channel)

	joinMSg = f"{users[addr].username} joined the channel."
	joinMSg = f"PRIVMSG {users[addr].channel.name} :{joinMSg}"
	sendChannelMessage(users[addr].username, joinMSg, users[addr].channel.name, True)

def removeFromChannel(user: User) -> None:
	if user.channel == None: return
	user.channel.users.remove(user)
	if len(user.channel.users) == 0:
		channels.pop(user.channel.name)
		


def executeQuit(addr, cmd : Command):
	if cmd.params['quitmessage'] == "": 
		quitMsg = f"{users[addr].username} quit."
	else:
		quitMsg = f"{users[addr].username} quit with message \"{cmd.params['quitmessage']}\"."

	quitMsg = f"PRIVMSG {users[addr].channel.name} :{quitMsg}"
	sendChannelMessage(users[addr].username, quitMsg, users[addr].channel.name, True)
	removeFromChannel(users[addr])

def executePart(addr, cmd : Command):
	if users[addr].channel == None: return
	if cmd.params['channel'] != users[addr].channel.name: return

	partMsg = f"{users[addr].username} left the channel."
	partMsg = f"PRIVMSG {users[addr].channel.name} :{partMsg}"
	sendChannelMessage(users[addr].username, partMsg, users[addr].channel.name, True)
	removeFromChannel(users[addr])

def executeList(addr, cmd : Command):
	msg = ""
	for channelName in channels:
		nUsers = len(channels[channelName].users)
		userStr = "user" if nUsers == 1 else "users" 
		msg += f"{channelName}: {nUsers} {userStr}.\n"

	msg = f"PRIVMSG {users[addr].username} :{msg}"
	users[addr].userSocket.send(msg.encode())

def executeWho(addr, cmd : Command):
	pass

def handleMessage(msgPair) -> None:
	addr, msg = msgPair
	cmd = parseMessage(msg)

	if cmd.cmdType == CmdType.USER: executeUser(addr, cmd)
	elif cmd.cmdType == CmdType.NICK: executeNick(addr, cmd)
	elif cmd.cmdType == CmdType.PRIVMSG: executePrivmsg(addr, cmd)
	elif cmd.cmdType == CmdType.JOIN: executeJoin(addr, cmd)
	elif cmd.cmdType == CmdType.QUIT: executeQuit(addr,cmd)
	elif cmd.cmdType == CmdType.PART: executePart(addr,cmd)
	elif cmd.cmdType == CmdType.LIST: executeList(addr,cmd)
	elif cmd.cmdType == CmdType.WHO: executeWho(addr,cmd)

while True:
	if msgQueue.empty(): continue

	handleMessage(msgQueue.get())