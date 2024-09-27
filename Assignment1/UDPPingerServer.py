# We will need the following module to generate randomized lost packets
import time
import random
from socket import *

serverName = "localhost"
serverPort = 12000
serverAddress = (serverName, serverPort)
# Create a UDP socket
# Notice the use of SOCK_DGRAM for UDP packets
serverSocket = socket(AF_INET, SOCK_DGRAM)
# Assign IP address and port number to socket
serverSocket.bind(('', serverPort))
while True:
    # Generate random number in the range of 0 to 10
    rand = random.randint(0, 10)
    # Receive the client packet along with the address it is coming from
    message, clientAddress = serverSocket.recvfrom(1024)
    # Capitalize the message from the client
    modifiedMessage = message.decode('utf-8').upper().encode('utf-8')
    # If rand is less is than 4, we consider the packet lost and do not respond
    if rand < 4:
        continue
    # Otherwise, the server responds
    serverSocket.sendto(modifiedMessage, clientAddress)