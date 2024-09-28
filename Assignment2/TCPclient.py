import sys
from socket import *

# Ensure the correct number of command-line arguments are provided
if len(sys.argv) != 4:
    print("Usage: client.py server_host server_port filename")
    sys.exit()

# Extract command-line arguments
serverName, serverPort, filepath = sys.argv[1:]
serverPort = int(serverPort)

# Create a TCP client socket
clientSocket = socket(AF_INET, SOCK_STREAM)

# Establish connection to the server
try:
    clientSocket.connect((serverName, serverPort))
    print(f"> Connection established with server {serverName} on port {serverPort}")
except error as connection_error:
    print(f"Error connecting to server: {connection_error}")
    sys.exit()

# Construct the HTTP (GET) request 
request_line = f"GET /{filepath} HTTP/1.1\r\n"
clientSocket.send(request_line.encode())
# Construct the HTTP request header
request_header_info = {
    "Host": f"{serverName}:{serverPort}",
    "User-Agent": "TCPClient/1.0",
    "Accept": "text/html",
}
request_header = "".join([f"{key}: {value}\r\n" for key, value in request_header_info.items()]) + "\r\n"
clientSocket.send(request_header.encode())

# Receive the response from the server
HTTP_response_message = ""
while True:
    received_data = clientSocket.recv(2048).decode()
    if not received_data:
        break
    HTTP_response_message += received_data

# Print the server's HTTP response
print(f"> --------Server Response--------\n{HTTP_response_message}")

# Close the connection
clientSocket.close()
print("> Connection closed.")
