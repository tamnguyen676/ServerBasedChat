import socket
import threading

# Object which represents a server
class ChatServer:

    def __init__(self):
        self.welcomingPort = 8888
        # These are the sockets that will be regulated to clients
        # UPDATE: onlineSockets holds a dictionary containing online sockets
        self.onlineSockets = {'1':None, '2':None, '3':None, '4':None, '5':None}
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_socket.bind((socket.gethostname(), self.welcomingPort))
        self.listen_socket.listen(5)

    # This function will accept a connection from the welcoming socket and create a new 
    # socket for the connection
    def acceptConnection(self):
        client_socket, client_address = self.listen_socket.accept()
        return client_socket    #Returns the new socket for the connection

    # Sends data to a given client index; data should be bytes
    # Assumes client exists
    def send(self, data, client_socket):
        client_socket.send(data.encode())
        print('SENT')

    # Receive something from a client index and returns as bytes
    # Assumes client exists
    def receive(self, client_socket):
        return client_socket.recv(2048).decode()

# This function is run in a new thread
def connection(server,client_socket):

    # Outer loop waits for HELLO command only
    while True:
        msg = server.receive(client_socket) # Message received from the program
        clientID = waitForHello(client_socket, msg, server)

        # Waits for CHAT_REQUEST command (should wait for others too)
        while True:
            msg = server.receive(client_socket) # Blocking
            if msg.split()[0] == 'CHAT_REQUEST':
                destID = msg.split()[1] # Stores id of Client B
                if destID in server.onlineSockets.keys() and server.onlineSockets[destID] is not None: #If client exists and is online
                    server.send('CHAT_STARTED({0},{1})'.format(getSessionID(clientID, destID), destID), client_socket)
                    print('Client {0} initiated chat with client {1}'.format(clientID,destID))

                    while True:
                        msg = server.receive(client_socket)

                        if msg != "":
                            server.send(msg,server.onlineSockets[destID])

                else:
                    server.send('UNREACHABLE {0}'.format(destID),client_socket)
                    print('Client {0} is not connected.'.format(destID))


def waitForHello(client_socket, msg, server):
    if msg.split()[0] == 'HELLO':  # Establishes initial connection when the HELLO message is received
        clientID = msg.split()[1]
        if clientID in server.onlineSockets.keys():  # To-do: Make sure this doesn't crash program
            server.send('CONNECTED', client_socket)  # Send CONNECTED response to client

            server.onlineSockets[clientID] = client_socket  # Keeps a dictionary of sockets that are online
            print('Successfully connected to client {0}'.format(clientID))
            return clientID
        else:
            server.send('DECLINED', client_socket)
            print('Declined client with id {0}'.format(clientID))




# Uniform way of generating session ID's.
# For example, client 1 connected to client 2 and client 2 to client 1 both result in id "1to2"
def getSessionID(ses1,ses2):
    if int(ses1) < int(ses2):
        return ses1 + 'to' + ses2

    return ses2 + 'to' + ses1


# Main function, it starts the thread that receives messages, then blocks with the acceptConnection() method
if __name__ == '__main__':
    print("Running Server...")
    server = ChatServer()
    while True:
        client_socket = server.acceptConnection()
        thread = threading.Thread(target=connection, args=(server, client_socket))
        thread.start()