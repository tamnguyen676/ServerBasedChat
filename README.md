# ServerBasedChat
Server Based Chat Using Python

This branch implements a simple server. ChatDriver demos the two python classes by sending a message from one client object to another.

Client index will be assigned in the order that chat clients connect. For example, the first client to connect will be Client A and will have a client index of 0. The second client will be Client B and will have a client index of 1, etc...

All connections are only implemented in TCP for the time being

It is assumed that ChatServer.py, ChatClient.py, and ChatDriver.py are all in the same directory.

The code should be fairly self-explanatory. Let me know if you want me to change anything/don't understand the code.

Class ChatServer:

  acceptConnection: You must run this function after intializing a client to accept their connection.
  
  send: Sends a sequence of bytes to a client index(0 = client A; 1 = client B etc)
  
  receive: Receive a sequence of bytes from a given client index

Class ChatClient:

  send: Sends a sequence of bytes from the client to the server
  
  receive: Receive a sequence of bytes from the server


***************HOW TO USE THE CODE***************
To start the server run the ChatServer.py script.

For each client, run a Client.py script

For each Client script:
1) Enter log on [CLIENT_ID]
2) If you would like to send a chat request enter "chat [client ID of the person you want to chat with]" *OR* enter "history [client ID of self to client chat history you would like to see]
3) Once you enter chat, chat away!
4) When you're done enter "End Chat"
5) You can then log back on and proceed from step 2
