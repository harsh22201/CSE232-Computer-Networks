#import socket module
from socket import *
from datetime import datetime
import sys
from Utils import get_ipv4_address
from threading import Thread

# Function to handle each client connection
def handle_client(connectionSocket, clientAddress, Thread_count):
    print(f"T{Thread_count}> Connection established with client {clientAddress[0]} on port {clientAddress[1]}")
    # Receive the HTTP (GET) request from the browser/TCPclient
    HTTP_request = connectionSocket.recv(2048).decode() 
    if(not HTTP_request):
        print (f"T{Thread_count}> Empty request received. Connection Aborted.")
        return
    print(f"T{Thread_count}> --------HTTP Request Message--------\n{HTTP_request}")
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
    print(f"T{Thread_count}> Response message sent successfully!")
    # After serving the request, we close the connectionSocket to the client
    connectionSocket.close()
    print(f"T{Thread_count}> Connection closed.")

# Main server function
def start_server():
    serverName = get_ipv4_address()  # The IP address of the server (localhost)
    serverPort = 12000
    serverSocket = socket(AF_INET, SOCK_STREAM)  # TCP socket
    
    # Bind to a specific address and port
    serverSocket.bind((serverName, serverPort))
    
    # Listen for TCP connection requests from the client
    serverSocket.listen(5)  # Set to 5 to allow up to 5 queued connections

    Thread_count = 0

    print("The server is ready to receive...")
    while True:
        # Accept new client connection
        connectionSocket, clientAddress = serverSocket.accept()
        # Create a new thread to handle the client's request
        Thread_count += 1
        client_thread = Thread(target=handle_client, args=(connectionSocket, clientAddress, Thread_count))
        client_thread.start()
    
    serverSocket.close()

if __name__ == "__main__":
    try:
        start_server()
    except KeyboardInterrupt:
        print("Server shutting down...")
        sys.exit()
