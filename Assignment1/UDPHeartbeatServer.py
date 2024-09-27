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
    # time received
    time_received = time.time()
    # decode the message and get the sequence number and time sent
    message = message.decode('utf-8').split()
    sequence_number = int(message[1])
    # convert the time sent form ctime to float
    time_sent = float(message[2])
    # delay in ms
    time_difference = (time_received - time_sent)*1000
    modifiedMessage = f"Ping {sequence_number} time difference={time_difference:.3f}ms".encode('utf-8')
    # If rand is less is than 4, we consider the packet lost and do not respond
    if rand < 4:
        continue
    # Otherwise, the server responds
    serverSocket.sendto(modifiedMessage, clientAddress)