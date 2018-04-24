import socket
import threading
import sqlite3
import time

# Object which represents a server
class ChatServer:
    def __init__(self):
        self.welcomingPort = 8888
        # These are the sockets that will be regulated to clients
        # UPDATE: onlineSockets holds a dictionary containing online sockets
        # This is also the valid clientIDs: 1-5 currently

        # Must change this line: if int(clientID) < 1 or int(clientID) > 5:
        # in connection() if we want to adjust the clientIDs
        # This line as well: for x in range(1,6)
        # A lot of other lines..... It's probably best if we don't change this
        self.onlineSockets = {'1':None, '2':None, '3':None, '4':None, '5':None}
        # Initialize dictionary of online sessions to a nonexistent session
        self.onlineSessions = {'-99to-98':None}
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_socket.bind((socket.gethostname(), self.welcomingPort))
        self.listen_socket.listen(5)

    # This function will accept a connection from the welcoming socket and create a new 
    # socket for the connection
    def acceptConnection(self):
        clientSocket, client_address = self.listen_socket.accept()
        return clientSocket    #Returns the new socket for the connection

    # Sends data to a given client index; data should be bytes
    # Assumes client exists
    def send(self, data, clientSocket):
        clientSocket.send(data.encode())

    # Receive something from a client index and returns as bytes
    # Assumes client exists
    def receive(self, clientSocket):
        try:
            return clientSocket.recv(2048).decode()
        except ConnectionResetError:
            print('Connection from client {0} has closed.'.format(getClientIdFromSocket(clientSocket)))
            self.onlineSockets[getClientIdFromSocket(clientSocket)] = None

# This function is run in a new thread
# It handles all connection requests from clients
def connection(server,clientSocket):

    #for testing
    print('A thread has been spawned in the server!')
    # Receive hello message then process it in waitForHello
    msg = server.receive(clientSocket) # Message received from the program
    clientID = waitForHello(clientSocket, msg, server)
    #for testing
    print('hello for client' + str(clientID))

    # We break and end this thread if the client requests an invalid connection
    if int(clientID) < 1 or int(clientID) > 5:
        #Reject this connection if an invalid clientID is used
        return

    # Waits for CHAT_REQUEST command

    # At this point, the connection can receive a chat request from one of the clients
    # or receive a CHAT_STARTED echo message from the client ie the client echoes back
    # the CHAT_STARTED message received from the server

    msg = server.receive(clientSocket)

    if msg != None:
        if msg.split()[0] == 'CHAT_REQUEST':
            destID = msg.split("(")[1][:-1] # Stores id of Client B

            #Will reject chat request if the destination is involved in another session
            inAnotherSession = True
            while inAnotherSession:
                inAnotherSession = False
                for x in server.onlineSessions:
                    #Checks if destination is in onlineSessions and if the session is Active
                    if str(destID) in x and server.onlineSessions[x] == 'Active':
                        inAnotherSession = True
                        server.send('UNREACHABLE {0}'.format(destID), clientSocket)
                        #for testing
                        print('destID in another session')
                        msg = server.receive(clientSocket)
                        destID = msg.split()[1]
            #for testing
            print('The destination is not in another session')

            #Will loop until a valid chat request is given
            while destID in server.onlineSockets.keys() and server.onlineSockets[destID] is None:
                server.send('UNREACHABLE {0}'.format(destID), clientSocket)
                print('Client {0} is not connected or is in another chat session.'.format(destID))
                print('Waiting for connection request with an available client')
                msg = server.receive(clientSocket)
                destID = msg.split()[1]

            #You can't request to chat yourself
            while destID == clientID:
                server.send('UNREACHABLE {0}'.format(destID), clientSocket)
                #for tseting
                print('Quit trying to chat with yourself')
                msg = server.receive(clientSocket)
                destID = msg.split()[1]


            destSocket = server.onlineSockets[destID]
            #UPDATE: Changes parenthesis to spaces
            # For ease of implementation, we will assume that CHAT_REQUEST will always result in a chat session
            # Start chat once both clients have been confirmed to be online
            server.send('CHAT_STARTED ({0},{1})'.format(getSessionID(clientID, destID), destID), clientSocket)
            server.send('CHAT_STARTED ({0},{1})'.format(getSessionID(clientID, destID), clientID), destSocket)
            # Create a new entry in onlineSessions
            server.onlineSessions[getSessionID(clientID, destID)] = 'Active'
            print('Client {0} initiated chat with client {1}'.format(clientID,destID))

            # This thread handles transferring this thread's incoming messages
            b_to_a_forwarding_thread = threading.Thread(target=b_to_a_forwarding,
                                                        args=(clientID, destID))
            b_to_a_forwarding_thread.start()

            #This consumes the chat_started thing
            server.receive(clientSocket)

            #This thread handles sending this connection's outgoing messages
            while True:
                msgFromA = server.receive(clientSocket)

                if "CHAT" in msgFromA:
                    msgFromA = msgFromA.split(',')[1][:-1] # CHAT (sessionID,This is the message)
                elif "END_REQUEST" in msgFromA:
                    print("a sent end notif")
                    server.onlineSessions[getSessionID(clientID, destID)] = None
                    server.send("END_NOTIF ({0})".format(getSessionID(clientID, destID)), clientSocket)
                    server.send("END_NOTIF ({0})".format(getSessionID(clientID, destID)), destSocket)
                    break

                #for testing
                print('Waiting for A')
                print(msgFromA)
                if msgFromA != "":
                    # Log the messages before sending
                    sqlCommand = "INSERT INTO log VALUES (\"{0}\",{1},\"{2}\")".format(getSessionID(clientID,destID),clientID,
                                                                               msgFromA)
                    cursor.execute(sqlCommand)
                    db.commit()

                    server.send(msgFromA, destSocket)
                #Handle shutting down session here
        elif msg.split()[0] == "HISTORY_REQ":
            destID = msg.split("(")[1][:-1] # The ID of the chat you want to see a history of
            sessionID = getSessionID(clientID,destID) # Session ID of the chat
            sqlCommand = 'SELECT source,message FROM log WHERE sessionID=\'{0}\''.format(sessionID)
            cursor.execute(sqlCommand)
            log = cursor.fetchall() #Contains a list of chat info

            for record in log:
                sendingID = record[0] # The source of the message
                message = record[1] # The contents of the message
                server.send('HISTORY_RESP ({0},{1})'.format(sendingID,message),clientSocket)
                time.sleep(.05)  # I don't know why, but if you delete this, things will break
        else:
            #This code runs if this connection is the chat requestee
            #for testing
            print('This is the chat_started thread')


#This thread will forward incoming messages to the connection
def b_to_a_forwarding(clientID,destID):
    #for testing
    print('btoa starts')

    clientSocket = server.onlineSockets[clientID]
    destSocket = server.onlineSockets[destID]
    while True:
        #for testing
        print('Waiting for B')

        msgFromB = server.receive(destSocket)

        if "CHAT" in msgFromB:
            msgFromB = msgFromB.split(',')[1][:-1]
        elif "END_REQUEST" in msgFromB:
            print("b sent end notif")
            server.onlineSessions[getSessionID(clientID, destID)] = None
            server.send("END_NOTIF ({0})".format(getSessionID(clientID, destID)), clientSocket)
            server.send("END_NOTIF ({0})".format(getSessionID(clientID, destID)), destSocket)
            break

        print(msgFromB)

        if msgFromB != "":
            sqlCommand = "INSERT INTO log VALUES (\"{0}\",{1},\"{2}\")".format(getSessionID(clientID, destID), destID,
                                                                       msgFromB)
            cursor.execute(sqlCommand)
            db.commit()
            server.send(msgFromB, clientSocket)


# Processes and returns the client ID if valid
# Returns a negative number if the client ID is invalid
def waitForHello(clientSocket, msg, server):
    if msg.split()[0] == 'HELLO':  # Establishes initial connection when the HELLO message is received
        clientID = msg.split()[1]
        if clientID in server.onlineSockets.keys() and server.onlineSockets[clientID] == None:  # To-do: Make sure this doesn't crash program
            server.send('CONNECTED', clientSocket)  # Send CONNECTED response to client

            server.onlineSockets[clientID] = clientSocket  # Keeps a dictionary of sockets that are online
            print('Successfully connected to client {0}'.format(clientID))
            return clientID
        else:
            server.send('DECLINED', clientSocket)
            print('Declined client with id {0}'.format(clientID))
            return '-1'



# Uniform way of generating session ID's.
# For example, client 1 connected to client 2 and client 2 to client 1 both result in id "1to2"
def getSessionID(ses1,ses2):
    if int(ses1) < int(ses2):
        return str(ses1) + 'to' + str(ses2)

    return str(ses2) + 'to' + str(ses1)

def getClientIdFromSocket(clientSocket):
    for id,socket in server.onlineSockets.items():
        if socket == clientSocket:
            return id

# Main function, it starts the thread that receives messages, then blocks with the acceptConnection() method
if __name__ == '__main__':
    #Creates the database and table
    db = sqlite3.connect("chatHistory.db",check_same_thread=False)
    cursor = db.cursor()

    createTable = """CREATE TABLE IF NOT EXISTS log (
    sessionID text,
    source int,
    message text);"""

    cursor.execute(createTable)

    print("Running Server...")
    server = ChatServer()
    while True:
        clientSocket = server.acceptConnection()
        thread = threading.Thread(target=connection, args=(server, clientSocket))
        thread.start()