from ChatClient import ChatClient
from threading import Thread, Lock
import threading
import _thread
import time
import sys

chatMode = False
#placeholder value for clientID; should be explicitly set during log in
clientID = 0
destID = 0
# Forces client to wait for server response before initiating chat
servReqMutex = Lock()
# Use this to ensure main acquires servReqMutex when it is released
# This is a bit complicated but it works
servReqMutex2 = Lock()
# Client must wait for chat to end for new Log on to commence
# Release whenever Log off happens
newChatMutex = Lock()
receivedEndChat = None   # if this is false, it means that this client typed log off. If true, it means the other client logged off
historyReqID = None # Global variable, used when history is requested to find id of requested chat


def connectToServer():
    global client, msg
    client = ChatClient()
    #for testing
    #print(clientID)
    client.send('HELLO {0}'.format(clientID))
    msg = client.receive()  # Blocking. Waits for server response
    if msg == 'CONNECTED':
        print('Connected Successfully!')
        return True
    elif msg == 'DECLINED':
        print('Server failed to verify client.')
        return False

# Listens for CHAT_REQUEST or CHAT_STARTED
# Breaks once chat has started
def protocolListen(client):
    global chatMode, chatStarted
    while True:
        servReqMutex.acquire() #Ensures that client must wait for server response before starting chat
        #for testing
        try:
            protocolMessage = client.receive()
        except ConnectionAbortedError:  # If the ocnnection no longer exists, break out of the loop and end thread
            break

        if 'CHAT_STARTED' in protocolMessage:
            chatMode = True

            sessionID = protocolMessage.split()[1].split(',')[0][1:]
            destID = protocolMessage.split(',')[1][:-1]

            servReqMutex.release()

            #Echo the CHAT_STARTED message
            client.send(protocolMessage)

            enterChatMode(client, destID, sessionID)
            #print('In chat started protocol')
            #should only stop listening once we receive CHAT_STARTED
        elif 'UNREACHABLE' in protocolMessage:
            #for testing
            print('Client {0} is either offline or in another chat session.'.format(protocolMessage.split('(')[1][:-1]))
            servReqMutex.release()
        elif 'HISTORY_RESP' in protocolMessage:
            global historyReqID
            sendingID = protocolMessage.split('(')[1].split(',')[0]
            sessionID = getSessionID(clientID, historyReqID)
            message = protocolMessage.split(',')[1][:-1]
            print('<{0}> <from: {1}> <{2}>'.format(sessionID,sendingID,message))
            servReqMutex.release()


        #This is here to make sure this thread doesn't immediately acquire serReqMutex
        # so the main thread has a chance to acquire it
        servReqMutex2.acquire()
        servReqMutex2.release()
        # For testing
        #print('2 catch/release')

#Prints out incoming messages
def messageListen(client,destID):
    global receivedEndChat, chatMode
    while True:
        receivedMessage = client.receive()

        if receivedMessage != "" and "END_NOTIF" not in receivedMessage.split()[0]:
            #Erases the current line, prints the new message, and reprints the input() message
            print("", end="\r")
            print("Client {0}: {1}".format(destID,receivedMessage))
            print("Client {0}: ".format(clientID), end="")
            sys.stdout.flush()
        #End the 
        elif "END_NOTIF" in receivedMessage.split()[0]:
            #print("", end="\r")
            print("\nChat Ended")
            chatMode = False

            if receivedEndChat or receivedEndChat == None:
                print('Please press enter twice to continue')
                receivedEndChat = True


            newChatMutex.release()
            break

def enterChatMode(client,destID,sessionID):
    global chatMode, receivedEndChat

    print('', end='\r')
    sys.stdout.flush()

    messageListenThread = threading.Thread(target=messageListen, args=(client,destID))
    messageListenThread.start()

    print('\nChat started with client {0}. Type "End Chat" to end.'.format(destID))
    while chatMode:
        messageToSend = input('Client {0}: '.format(clientID))

        if receivedEndChat == True:
            newChatMutex.release()
            receivedEndChat = False
            break

        if messageToSend.lower().strip() == 'end chat'.lower().strip():
            client.send("END_REQUEST ({0})".format(sessionID))
            chatMode = False
            receivedEndChat = False  # This client caused the chat to end
            break

        client.send('CHAT ({0},{1})'.format(sessionID,messageToSend))

def getSessionID(ses1,ses2):
    if int(ses1) < int(ses2):
        return str(ses1) + 'to' + str(ses2)

    return str(ses2) + 'to' + str(ses1)

# TODO: figure out how to make this run multiple times
if __name__ == '__main__':
    while True:
        newChatMutex.acquire()
        #This will help enterChatMode thread exit when we receive a log off notification
        if receivedEndChat:  # Might need to rename
            print('Press enter to continue...')

        # This block waits for the log on command
        # Should enter 'Log on [clientID]
        command = input('Enter command (\"Log on [clientID]\"): ')

        #Check if 'Log on' was entered
        while 'log on' not in command.lower() or len(command.split()) != 3:
            command = input('You must enter Log on [Client ID] to continue: ')

        # Assumes clientID will be an int
        clientID = command.split()[2]

        #for testing clientID
        #print('we got da clientid {0}'.format(clientID))

        # If we send an invalid clientID, request a valid one til we get a connection
        while connectToServer() != True:
            clientID = input('Please enter a valid clientID: ')

        # Now that we're connected, we start listening for CHAT_REQUESTs or CHAT_STARTEDs
        protocolListenThread = threading.Thread(target=protocolListen, args=(client,))
        protocolListenThread.start()

        newChatMutex.release()  # Temporarily releases lock so it can be acquired in the next command
        while True:
            newChatMutex.acquire()

            command = input('Please enter a command: ')

            if receivedEndChat:
                print('Please press enter one more time.')
                newChatMutex.acquire()
                newChatMutex.acquire()  # I am not sure why I need to acquire twice, but it works

            # The "command" was actually supposed to be a message if we are in chat mode. Send it as such
            if chatMode:
                messageToSend = command
                sessionID = getSessionID(clientID, destID)   # destID should be set globally when chatMode was entered
                if messageToSend.lower().strip() == 'end chat'.lower().strip():
                    client.send("END_REQUEST ({0})".format(sessionID))
                    chatMode = False
                    newChatMutex.release()
                    receivedEndChat = False # This client caused the chat to end
                    continue
                client.send('CHAT ({0},{1})'.format(sessionID, messageToSend))
                print('Client {0}: '.format(clientID))
            else:
                if "chat" in command.lower():
                    # Only loop this while chatMode is not activated
                    # Waiting for chat initiation or request to chat from protocolListenThread
                    while True:
                        destID = command.split()[1]
                        #Let user know we are waiting on chat request response
                        client.send('CHAT_REQUEST ({0})'.format(destID))

                        servReqMutex2.acquire()
                        #for testing
                        #print('acquire 2 in main')
                        servReqMutex.acquire() # Waits for protocolListen to receive confirmation that chat session has begun
                        servReqMutex.release()

                        if chatMode:
                            break

                        # If you get here then the Client is unreachable
                        print('Client {0} unreachable'.format(command.split()[1]))
                        servReqMutex2.release()
                        break
                elif 'history' in command.lower(): # Move this later
                    historyReqID = command.split()[1]
                    client.send('HISTORY_REQ ({0})'.format(historyReqID))
                    if servReqMutex2.locked():
                        servReqMutex2.release()
                elif command.lower() == 'log off':
                    if newChatMutex.locked():
                        newChatMutex.release()

                    client.close()

                    break
                if not chatMode and newChatMutex.locked():
                    newChatMutex.release()