import socket

serverName = "127.0.0.1"
serverPort = 1150

msg: str = input("Enter some text: ")

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSocket.sendto(msg.encode(), (serverName, serverPort))

newMsg, serverAddress = clientSocket.recvfrom(2048)

print(newMsg.decode())

clientSocket.close()