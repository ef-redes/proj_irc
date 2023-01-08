import socket
import threading
import constants
from parse import *

currentChannel : str = ""

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

	currentChannel = cmd.params['channel']
	print(f"Joined {cmd.params['channel']} channel.")

def handleMessage(msg: str):
	cmd = parseMessage(msg)

	if cmd.cmdType == CmdType.PRIVMSG: executePrivmsg(cmd)


messageThread = threading.Thread(target=listenMessages, daemon=True)
messageThread.start()

def processInput(msg : str) -> str:
	if msg[0] != "/": return f"PRIVMSG {currentChannel} :{msg}"
	cmd = parseMessage(msg[1:])

	if cmd.cmdType == CmdType.JOIN: executeJoin(cmd)

	return msg[1:]


while True:
	msg = processInput(input())
	clientSocket.send(msg.encode())