from ChatClient import ChatClient
import threading


def connectToServer():
    global client, msg
    client = ChatClient()
    client.send('HELLO {0}'.format(clientID))
    msg = client.receive()  # Blocking. Waits for server response
    if msg == 'CONNECTED':
        print('Connected Successfully!')
    elif msg == 'DECLINED':
        print('Server failed to verify client.')

def receive(client,destID):
    while True:
        receiveMessage = client.receive()

        if receiveMessage != "":
            print("Client {0}: {1}".format(destID,receiveMessage))


if __name__ == '__main__':
    clientID = 1

    # This block waits for the log on command
    while True:
        command = input('Enter command: ')

        if command.capitalize().strip() == 'Log on'.capitalize().strip(): # Initiate connection when user types log on
            client = ChatClient()
            connectToServer()
        else:
            continue

        # This block waits for other commands
        while True:
            command = input('Enter command: ').capitalize().strip()

            if command.split()[0] == 'Chat'.capitalize().strip():
                destID = command.split()[1]
                client.send('CHAT_REQUEST {0}'.format(destID))
                msg = client.receive()

                if 'CHAT_STARTED' in msg:
                    print('Chat started with client {0}. Type "Log Off" to end.'.format(command.split()[1]))
                    receiveThread = threading.Thread(target=receive, args=(client, destID))
                    receiveThread.start()
                    while True:
                        msgSend = input("Client {0}: ".format(clientID))
                        client.send(msgSend)

                else:
                    print('Could not start chat with client {0}'.format(command.split()[1]))

            # NOT DONE
            if command == 'Log off'.capitalize().strip():
                client.close()