import socket, threading

# Object which represents a server
class ChatServer:
    def __init__(self):
        self.welcomingPort = 8888
        #These are the sockets that will be regelated to clients
        self.clientSockets = []
        self.currentClient = 1  #UPDATE: Changed from letters to number
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_socket.bind((socket.gethostname(), self.welcomingPort))
        self.listen_socket.listen(5)

    # This function will accept a connection from the welcoming socket and create a new 
    # socket for the connection
    # Could eventually implement this asynchronously
    def acceptConnection(self):
        client_connection, client_address = self.listen_socket.accept()
        # Add new client socket empty clientSocets list
        self.clientSockets.append(client_connection)
        print("Congratulations client " + str(self.currentClient) + ", you have connected to the server!")
        self.currentClient += 1

    # Sends data to a given client index; data should be bytes
    # Assumes client exists
    def send(self, data, client):
        self.clientSockets[client].send(data.encode())  #UPDATE: Function automatically encodes

    # Receive something from a client index and returns as bytes
    # Assumes client exists
    def receive(self, client):
        if len(self.clientSockets) > client:
            return self.clientSockets[client].recv(2048)
        else:
            return

#This function is run in a new thread
def process(server):
    newMsg = None
    while (True):
        msg = server.receive(0)

        if (newMsg != msg):
            print(msg)
            newMsg = msg


#Main function, it starts the thread that receives messages, then blocks with the acceptConnection() method
if __name__ == '__main__':
    print("Running Server...")
    server = ChatServer()

    thread = threading.Thread(target=process,args=(server,))
    thread.start()

    print("Waiting for connections...")
    server.acceptConnection()