import socket

serverPort = 1150
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind(('', serverPort))

while True:
	msg, clientAddress = serverSocket.recvfrom(2048)
	print(f"Request from {clientAddress[0]}")
	newMsg = msg.decode().upper()
	serverSocket.sendto(newMsg.encode(), clientAddress)