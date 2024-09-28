import socket

def get_ipv4_address():
    try:
        # Create a socket and connect to an external IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Google Public DNS IP 
        # We don't send any data, Only connection is made to determine the local IP address used for routing.
        ip_address = s.getsockname()[0]
    except Exception as e:
        ip_address = str(e)
    finally:
        s.close()
    
    return ip_address

