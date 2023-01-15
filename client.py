import socket
import threading
import constants
from parse import *

currentChannel : str = ""
finishSession : bool = False

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((constants.serverAddress, constants.serverPort))

def listenMessages():
	while True:
		try:
			handleMessage(clientSocket.recv(constants.bufsize).decode())
		except:
			break

def executePrivmsg(cmd: Command):
	print(cmd.params["text"])

def executeJoin(cmd: Command):
	global currentChannel

	if cmd.params['channel'][0] == "#":
		if cmd.params['channel'] == currentChannel:
			print(f"Already in {currentChannel}.")
			return
		currentChannel = cmd.params['channel']
		print(f"Joined {currentChannel} channel.")
	else:
		print("Invalid channel name.")

def executeQuit(cmd: Command):
	global finishSession
	finishSession = True

def handleMessage(msg: str):
	cmd = parseMessage(msg)

	if cmd.cmdType == CmdType.PRIVMSG: executePrivmsg(cmd)


messageThread = threading.Thread(target=listenMessages, daemon=True)
messageThread.start()

def processInput(msg : str) -> str:
	if msg[0] != "/": return f"PRIVMSG {currentChannel} :{msg}"
	cmd = parseMessage(msg[1:])

	if cmd.cmdType == CmdType.JOIN: executeJoin(cmd)
	elif cmd.cmdType == CmdType.QUIT: executeQuit(cmd)

	return msg[1:]


while not finishSession:
	msg = processInput(input())
	clientSocket.send(msg.encode())