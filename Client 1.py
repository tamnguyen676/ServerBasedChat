from ChatClient import ChatClient

if __name__ == '__main__':
    clientID = 1

    # This block waits for the log on command
    while True:
        command = input('Enter command: ')

        if command.capitalize().strip() == 'Log on'.capitalize().strip(): # Initiate connection when user types log on
            client = ChatClient()

            client.send('HELLO {0}'.format(clientID))

            msg = client.receive()  # Blocking. Waits for server response

            if msg == 'CONNECTED':
                print('Connected Successfully!')
            elif msg == 'DECLINED':
                print('Server failed to verify client.')
                break # Ends the program if client couldn't be verified

        # This block waits for other commands
        while True:
            command = input('Enter command: ').capitalize().strip()

            # NOT DONE
            if command == 'Log off'.capitalize().strip():
                client.close()

            if command.split()[0] == 'Chat'.capitalize().strip():
                client.send('CHAT_REQUEST {0}'.format(command.split()[1]))
                msg = client.receive()

                if 'CHAT_STARTED' in msg:
                    print('Chat started with client {0}'.format(command.split()[1]))
                else:
                    print('Could not start chat with client {0}'.format(command.split()[1]))
                # Need to implement actual chat session