import socket
import constants

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((constants.serverAddress, constants.serverPort))

while True:
	msg = input()
	clientSocket.send(msg.encode())