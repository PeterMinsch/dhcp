#!/usr/bin/env python3
import uuid
import socket
import time
from datetime import datetime

# Time operations in python
# timestamp = datetime.fromisoformat(isotimestring)

def parse_acknowledge_message(message):
    # Decode the bytes message into a string
    message_str = message.decode("utf-8")
    
    # Split the message into parts
    parts = message_str.split()

    # Initialize variables for each field
    request = None
    mac = None
    ip = None
    timestamp = None

    # Extract the fields based on the number of parts in the message
    if len(parts) >= 1:
        request = parts[0]  # First part is always the request type
    if len(parts) >= 2:
        mac = parts[1][2:-1] if len(parts[1]) > 2 else None  # Extract MAC address if present
    if len(parts) >= 3:
        ip = parts[2] if len(parts[2]) > 0 else None  # Extract IP address if present
    if len(parts) >= 4:
        timestamp_str = " ".join(parts[3:]) if len(parts[3:]) > 0 else None  # Extract timestamp if present
        if timestamp_str:
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")  # Convert timestamp to datetime object

    # Return the parsed fields
    return request, mac, ip, timestamp

def getTimestamp():
    isotimestring = datetime.now().isoformat()
    return datetime.fromisoformat(isotimestring)

def display_menu():
    print("Menu:")
    print("1. Release")
    print("2. Renew")
    print("3. Quit")
    choice = input("Enter your choice: ")
    return choice

# Extract local MAC address [DO NOT CHANGE]
MAC = ":".join(["{:02x}".format((uuid.getnode() >> ele) & 0xFF) for ele in range(0, 8 * 6, 8)][::-1]).upper()

# SERVER IP AND PORT NUMBER [DO NOT CHANGE VAR NAMES]
SERVER_IP = "10.0.0.100"
SERVER_PORT = 9000


clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Sending DISCOVER message
message = "DISCOVER " + MAC
print("message is ", message)
clientSocket.sendto(message.encode(), (SERVER_IP, SERVER_PORT))
print(f"we sent the message out")
message, _ = clientSocket.recvfrom(4096)
# LISTENING FOR RESPONSE
print(f"message is {message}")
request, mac, ip, timestamp = parse_acknowledge_message(message)

if request == "OFFER":
    if mac == MAC:
        if timestamp < getTimestamp():
            pass
        else:
            message = "REQUEST" + MAC 
if request == "ACKNOWLEDGE":
    if mac == MAC:
        print(f"the current time is {getTimestamp()}")
        print(f"ip {ip} has been assigned to you and will expire at {timestamp}")
    else:
        print("Your request cannot be handled")


while True: 
        choice = display_menu()
        if choice == '1':  # Release
            timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            message = f"RELEASE {MAC} {ip} {timestamp_str}"
            print(f"Your IP {ip} has been released")
            clientSocket.sendto(message.encode(), (SERVER_IP, SERVER_PORT))
        elif choice == '2':  # Renew
            if timestamp:
                timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")
                message = "RENEW" + MAC + " " + ip + " " + timestamp_str
            else:
                message = "RENEW" + MAC + " " + ip + " " 
            clientSocket.sendto("RENEW".encode(), (SERVER_IP, SERVER_PORT))

            message, _ = clientSocket.recvfrom(4096)
            print(f"message is {message}")
            renew_request, renew_mac, renew_ip, timestamp = parse_acknowledge_message(message)
            print(f"Your ip {ip} has been renewed for 60 more secs")
        elif choice == '3':  # Quit
            print("Quitting the client program.")
            clientSocket.close()
            exit()
        else:
            print("Invalid choice. Please enter a valid option.")
message, _ = clientSocket.recvfrom(4096)
#print(f"message is {message}")
#print(f"_ is {_}")
clientSocket.close()
