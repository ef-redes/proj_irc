import socket

serverName = "177.133.58.252"
port = 1150

msg = input("Enter your message: ")

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((serverName, port))

clientSocket.send(msg.encode())
newMsg = clientSocket.recv(2048).decode()

print(newMsg)

clientSocket.close()