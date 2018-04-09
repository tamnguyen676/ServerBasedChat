import socket

# Class which represents a chat client
class ChatClient:
    def __init__(self):
        # create an INET, STREAMing socket
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverPort = 8888 #hard code the welcoming port of the server
        self.serverAddress = socket.gethostname() #hard code the address of the server here
        # now connect to the web server on port serverPort - an atypical connection port for testing
        self.clientSocket.connect((self.serverAddress, self.serverPort))


    # Data must be converted to bytes before sending; sends to server
    def send(self, data):
        self.clientSocket.send(data.encode()) #UPDATE: Function automatically encodes
        return

    # Returns a byte that was received from the server
    def receive(self):
        return self.clientSocket.recv(2048).decode()

    def close(self):
        self.clientSocket.close()