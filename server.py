import socket
import threading
import queue
import constants

debug = True

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind(('', constants.serverPort))

serverSocket.listen()

clients = {}

msgQueue = queue.Queue()

clientThreads = {}
def acceptClient():
	while True:
		try:
			connectionSocket, addr = serverSocket.accept()
			if debug: print(f"Accepted connection from {addr}.")

			clients[addr] = connectionSocket
			clientThreads[addr] = \
				threading.Thread(target=handleClient, args=(clients[addr],), daemon=True)
			clientThreads[addr].start()
		except OSError:
			break

def handleClient(connectionSocket: socket):
	if debug: print(f"Handling client {connectionSocket.getsockname()}.")
	while True:
		try:
			msgQueue.put(connectionSocket.recv(constants.bufsize))
		except:
			break


acceptThread = threading.Thread(target=acceptClient, daemon=True)
acceptThread.start()


while True:
	if msgQueue.empty(): continue

	msg = msgQueue.get().decode()
	if msg == "exit":
		for client in clients:
			client.close()
		
		serverSocket.close()
		break

	print(msg)