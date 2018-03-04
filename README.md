# ServerBasedChat
Server Based Chat Using Python

This branch implements a simple server. ChatDriver tests out functionality by sending a message from one client object to another.

Some notes: 
This code currently only works if it's run on one computer. We will need to hardcode in the server address and its welcoming 
port if we would like it to work on different machines.

Client index will be assigned in the order that chat clients connect. For example, the first client to connect will be Client A and will have a client index of 0. The second client will be Client B and will have a client index of 1, etc...

The code should be fairly self-explanatory. Let me know if you want me to change anything/don't understand the code.

Class ChatServer:

  acceptConnection: Should run this after intializing client to accept their connection
  send: Sends a sequence of bytes to a client index(0 = client A; 1 = client B etc)
  receive: Receive a sequence of bytes from a given client index

Class ChatClient:

  send: Sends a sequence of bytes from the client to the server
  receive: Receive a sequence of bytes from the server
