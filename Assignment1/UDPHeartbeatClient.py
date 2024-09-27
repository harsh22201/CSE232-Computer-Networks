import time
from socket import *

serverName = "localhost"
serverPort = 12000
serverAddress = (serverName, serverPort)

# Define the timeout value for the client to wait for a response from the server
TIME_OUT = -1
serverResponses = []

# Create a UDP clientSocket
clientSocket = socket(AF_INET, SOCK_DGRAM) # Notice the use of SOCK_DGRAM for UDP packets
# Set the timeout of to 1 second
clientSocket.settimeout(1)
Heartbeat = 3
print(f"PING {serverName} 10 times")
total_ping = 10
for sequence_number in range(1,total_ping+1):
    time_sent = time.time()
    message = f"Ping {sequence_number} {time_sent}".encode('utf-8')
    # Send the UDP packet with the ping message
    clientSocket.sendto(message,serverAddress)
    # Wait for the server to respond
    try:
        modifiedMessage, serverAddress = clientSocket.recvfrom(1024)
        modifiedMessage = modifiedMessage.decode('utf-8')
        time_received = time.time()
        rtt = (time_received - time_sent)*1000
        print(f"udp_seq={sequence_number} message=\"{modifiedMessage}\" rtt={rtt:.3f}ms")
        serverResponses.append(rtt)
        # reset the heartbeat
        Heartbeat = 3
    except timeout:
        print(f"udp_seq={sequence_number} Request timed out ")
        serverResponses.append(TIME_OUT)
        # decrement the heartbeat and check if the server applicaƟon has stopped
        Heartbeat -= 1
        if (Heartbeat == 0):
            print("Server is down")
            break

clientSocket.close()

# Calculate the statistics
# Report the minimum RTT, maximum RTT, average RTT, and packet loss rate at the end of all pings from the client
total_time = 0
packet_loss = 0
rtt_min = float('inf')
rtt_max = float('-inf')
for rtt in serverResponses:
    if rtt == TIME_OUT:
        packet_loss += 1
    else:
        total_time += rtt
        rtt_min = min(rtt_min,rtt)
        rtt_max = max(rtt_max,rtt)

packet_transmitted = len(serverResponses)
packet_received = packet_transmitted - packet_loss
packet_loss_rate = (packet_loss/packet_transmitted)*100
if packet_received == 0:
    rtt_avg = 0
else:
    rtt_avg = total_time/packet_received

print(f"\n--- {serverName} ping statistics ---")
print(f"{packet_transmitted} packets transmitted, {packet_received} received, {packet_loss_rate:.2f}% packet loss")
print(f"rtt min/avg/max = {rtt_min:.3f}/{rtt_avg:.3f}/{rtt_max:.3f} ms")

