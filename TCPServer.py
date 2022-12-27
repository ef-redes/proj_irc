import socket

serverName = "177.133.58.252"
port = 1150

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind(('', port))

serverSocket.listen(1)
while True:
	connectionSocket, addr = serverSocket.accept()
	print(f"Request from {addr}")

	msg = connectionSocket.recv(2048).decode()

	newMsg = msg.upper()

	connectionSocket.send(newMsg.encode())
	connectionSocket.close()