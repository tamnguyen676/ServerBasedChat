from ChatClient import ChatClient
import threading
import time

chatMode = False
clientID = 2

def connectToServer():
    global client, msg
    client = ChatClient()
    client.send('HELLO {0}'.format(clientID))
    msg = client.receive()  # Blocking. Waits for server response
    if msg == 'CONNECTED':
        print('Connected Successfully!')
    elif msg == 'DECLINED':
        print('Server failed to verify client.')

def protocolListen(client):
    global chatMode, chatStarted
    while True:
        protocolMessage = client.receive()

        if 'CHAT_REQUEST' in protocolMessage:
            chatMode = True
            destID = protocolMessage.split("(")[1][:-1]
            enterChatMode(client,destID)
            break
        elif 'CHAT_STARTED' in protocolMessage:
            chatMode = True


def messageListen(client,destID):
    while True:
        receivedMessage = client.receive()

        if receivedMessage != "":
            print("Client {0}: {1}".format(destID,receivedMessage))

def checkChatMode():
    global chatMode

    while chatMode == True:
        pass

def enterChatMode(client,destID):
    messageListenThread = threading.Thread(target=messageListen,args=(client,destID))
    messageListenThread.start()
    print('\nChat started with client {0}. Type "Log Off" to end.'.format(destID))
    while True:
        messageToSend = input('Client {0}: '.format(clientID))

        if messageToSend.capitalize().strip() == 'Log Off'.capitalize().strip():
            break

        client.send(messageToSend)

if __name__ == '__main__':


    # This block waits for the log on command
    while True:
        command = input('Enter command: ')

        if command.capitalize().strip() == 'Log on'.capitalize().strip(): # Initiate connection when user types log on
            connectToServer()
        else:
            continue

        protocolListenThread = threading.Thread(target=protocolListen, args=(client,))
        protocolListenThread.start()

        # This block waits for other commands
        while True:
            command = input('Enter command: ').capitalize().strip()

            checkChatMode()

            if command.split()[0] == 'Chat'.capitalize().strip():
                destID = command.split()[1]
                client.send('CHAT_REQUEST {0}'.format(destID))

                time.sleep(.2) # Waits for other thread to set flag. Maybe we can use locks instead somehow?
                if chatMode:
                    enterChatMode(client, destID)
                else:
                    print('Could not start chat with client {0}'.format(command.split()[1]))

            # NOT DONE
            if command == 'Log off'.capitalize().strip():
                client.close()