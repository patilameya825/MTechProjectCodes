#!/usr/bin/python           # This is client.py file

import socket               # Import socket module
while True:
	s = socket.socket()         # Create a socket object
	host = '192.168.0.103' # Get local machine name
	port = 5003                # Reserve a port for your service.
#s.connect((host,port))
#while True:
	s.connect((host, port))
	var = input('Enter number: ')
	var1 = var.encode()
	print(type(var1))
	s.send(var1)
	s.close                     # Close the socket when done
