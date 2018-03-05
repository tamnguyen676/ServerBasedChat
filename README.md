# ServerBasedChat
Server Based Chat Using Python

This branch implements a simple server. ChatDriver demos the two python classes by sending a message from one client object to another.

Some notes: 
This code currently only works if it's run on one computer. We will need to hardcode in the server address and its welcoming 
port if we would like it to work on different machines.

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
