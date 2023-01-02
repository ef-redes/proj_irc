import socket
import threading
import constants
from parse import *

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

def handleMessage(msg: str):
	cmd = parseMessage(msg)

	if cmd.cmdType == CmdType.PRIVMSG: executePrivmsg(cmd)


messageThread = threading.Thread(target=listenMessages, daemon=True)
messageThread.start()

while True:
	msg = input()
	clientSocket.send(msg.encode())