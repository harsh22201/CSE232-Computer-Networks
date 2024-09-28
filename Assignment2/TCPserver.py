#import socket module
from socket import *
from datetime import datetime
import sys
from Utils import get_ipv4_address

# Prepare a sever socket
serverName = get_ipv4_address()
serverPort = 12000  
serverSocket = socket(AF_INET, SOCK_STREAM) # In TCP, serverSocket will be our welcoming socket
serverSocket.bind((serverName, serverPort)) # Bind to a specific address and port
serverSocket.listen(1) # Make server listen for TCP connection requests from the client. The parameter specifies the maximum number of queued connections (at least 1).

print("> The server is ready to receive...")
while True:
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    # Establish the connection
    connectionSocket, clientAddress = serverSocket.accept() # Create a new connectionSocket in the server, dedicated to this particular client. 
    print(f"> Connection established with client {clientAddress[0]} on port {clientAddress[1]}")
    # Receive the HTTP (GET) request from the browser/TCPclient
    HTTP_request = connectionSocket.recv(2048).decode() 
    if(not HTTP_request):
        print ("> Empty request received. Connection Aborted.")
        continue
    print(f"> --------HTTP Request Message--------\n{HTTP_request}")
    # Extract the path of the requested object from the GET request
    filepath = HTTP_request.split()[1][1:] 
    try:
        # Open the file and read the content
        with open(filepath) as file:
            outputdata = file.read()
        status = "200 OK"
    except IOError:
        # Send response message for file not found
        with open("404.html") as file:
            outputdata = file.read()
        status = "404 Not Found"
    # Send HTTP response status line
    response_status = f"HTTP/1.1 {status}\r\n"
    connectionSocket.send(response_status.encode())
    # Send HTTP response header lines
    response_header_info = {
        "Date": f"{datetime.now().strftime('%a, %d %b %Y %H:%M:%S')}",
        "Server": "TCPServer/1.0",
        "Content-Length": len(outputdata),
        "Content-Type": "text/html",
    }
    response_header = "".join([f"{key}: {value}\r\n" for key, value in response_header_info.items()]) + "\r\n"
    connectionSocket.send(response_header.encode())
    # Send the content of the requested file to the client
    for i in range(0, len(outputdata)):
        connectionSocket.send(outputdata[i].encode())
    connectionSocket.send("\r\n".encode())
    print("> Response message sent successfully!")
    # After serving the request, we close the connectionSocket to the client
    connectionSocket.close()
    print("> Connection closed.")

serverSocket.close()
sys.exit() # Terminate the program after sending the corresponding data

# URL: http://192.168.105.194:12000/HelloWorld.html
