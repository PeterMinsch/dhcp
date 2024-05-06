import uuid
import socket
import time
from datetime import datetime

SERVER_IP = "10.0.0.100"
SERVER_PORT = 9000


clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

message = "LIST"
clientSocket.sendto(message.encode(), (SERVER_IP, SERVER_PORT))

message, _ = clientSocket.recvfrom(4096)

print(f"message is {message}")

clientSocket.close()