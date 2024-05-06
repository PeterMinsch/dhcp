#!/usr/bin/env python3
import socket
from ipaddress import IPv4Interface
from datetime import datetime, timedelta

# Time operations in python
# isotimestring = datetime.now().isoformat()
# timestamp = datetime.fromisoformat(isotimestring)
# sixty_sec_from_now = timestamp + timedelta(seconds=60)

# Choose a data structure to store your records
#records = [] or {} or object

class Record: #store record num, client mac, ip, timestamp, and ack
    currentRecordNum = 0
    def __init__(self, mac, ip, timestamp):
        Record.currentRecordNum += 1
        self.recordNum = Record.currentRecordNum
        self.mac = mac
        self.ip = ip
        self.timestamp = timestamp
        self.ack = True #True if awk, False if not awk

records = []
# List containing all available IP addresses as strings
ip_addresses = [ip.exploded for ip in IPv4Interface("192.168.45.0/28").network.hosts()]
available = [False] * len(ip_addresses)
# Parse the client messages

def checkIP(mac):
    i = 0
    for j in range(records):
        if records[i].mac == mac:
            break
        i += 1
    if available[i] == True:
        return False
    else:
        return True



def checkRecord(mac):#check if the mac address in the exists
    for record in records: 
            if mac == record.mac:
                return record
    return None
        
def checkRecordByIP(ip):
    for record in records:
        if ip == record.ip:
            return record
    return None
def getTimestamp():
    return datetime.now()

def getSixtyFromNow():
    return datetime.now() + timedelta(seconds=60)

def checkExpired():
    for record in records:
        if record.timestamp < getTimestamp():
            return record
    return None

def checkAvailable():
    i = 0
    for aval in available:
        if aval == False:
            return i
        i += 1

    return -1 

def parse_message(message):
    '''
    Parse the message into the request and additional information (MAC address, IP address, timestamp).
    '''
    parts = message.split()
    if len(parts) == 1:
        return parts[0], None, None, None
    if len(parts) >= 2:
        request_type = parts[0]
        mac_address = parts[1]
    else:
        return None, None, None, None
    
    if len(parts) >= 3:
        ip_address = parts[2]
    else:
        ip_address = None

    if len(parts) >= 4:
        timestamp = b' '.join(parts[3:])
    else:
        timestamp = None

    return request_type, mac_address, ip_address, timestamp

'''
DISCOVER: 
1. check if any ip has been assigned to the client
2. if the record is found then check if its expired 
    if not expired then set ack to True
        then send ack message to client
3. if the record is not found
    check if all the ips have not been assigned yet
    if all ips are assigned then check if there's an expired record
        if there is an expired ip then we will use that ip
            the server will update that record with new info
'''
# Calculate response based on message
def dhcp_operation(ip_counter, request, mac, clientAddress, ip):
    if request == b"LIST":
        if len(records) > 0:
            print("line 112")
            records_str = '\n'.join([str(record.__dict__) for record in records])
            records_bytes = records_str.encode()
            server.sendto(records_bytes, clientAddress)
        else:
            print("line 117")
            server.sendto("EMPTY".encode(), clientAddress)
    elif request == b"DISCOVER":
        
        flag = False
        
        recordFound = checkRecord(mac)

        if recordFound: #check if the timestamp is exists
            if recordFound.timestamp > getTimestamp(): 
                recordFound.ack = True
                message = f"ACKNOWLEDGE {recordFound.mac} {recordFound.ip} {recordFound.timestamp}"
                server.sendto(message.encode(), clientAddress)

            else: #if timestamp has expired
                recordFound.timestamp = getTimestamp()#update the timestamp to 60 secs from now
                recordFound.ack = False#update ack to false
                message = f"OFFER {recordFound.mac} {recordFound.ip} {recordFound.timestamp}"
                server.sendto(message.encode(), clientAddress)
                return
        else:
            if checkAvailable() == -1: #if no free ip then check exp of the records
                for record in records:
                    if record.timestamp >= record.expiration: #if record is expired
                        record.mac = mac #update mac
                        record.timestamp = getTimestamp #update timestamp
                        record.expiration = timestamp + timedelta(sec=60) #update expiration
                        record.ack = False #set ack to false
                        flag = True #expired record was found 
                        unoccupiedIP = records.ip #the server will use this ip for the new request
            else:
                # unoccupiedIP = ip_addresses[checkAvailable()]
                # available[checkAvailable()] = True
                # for record in records:
                #     if record.ip == unoccupiedIP:
                #         record.mac
                #         record.timestamp = getTimestamp()
                #         record.expiration = timestamp + timedelta(sec=60) #update expiration
                #         record.ack = False #set ack to false
                records.append(Record(mac, ip_addresses[checkAvailable()], getSixtyFromNow()))
                available[checkAvailable()] = True
                recordFound = checkRecord(mac)
                flag = True
                message = f"OFFER {recordFound.mac} {recordFound.ip} {recordFound.timestamp}"
                server.sendto(message.encode(), clientAddress)
            if flag == False: #theres no expired records and there is no ip
                server.sendto("DECLINE".encode(), clientAddress)    
            


        #send awk message to clinet containing the info

    elif request == b"REQUEST": #
        recordFound = checkRecord(mac)
        if recordFound:
            if recordFound.ip != ip:
                server.sendto("DECLINE".encode(), clientAddress)
            else:
                if recordFound.timestamp < recordFound.expiration:
                    server.sendto("DECLINE".encode(), clientAddress)
                else:
                    recordFound.ack = True
                    #server.sendto(("ACKKNOWLEDGE".encode(), recordFound.mac, recordFound.ip, recordFound.timestamp), clientAddress)
                    message = f"ACKNOWLEDGE {recordFound.mac} {ip_addresses[ip_counter]} {recordFound.timestamp}"
                    server.sendto(message.encode(), clientAddress)


        
                
    elif request == b"RELEASE": #send a release message to the server
        print("in release")
        recordFound = checkRecord(mac)
        if recordFound:
            recordFound.timestamp = getTimestamp()
            recordFound.ack = False
            available[records.index(recordFound)] = False
            records.remove(recordFound)
            server.sendto(request, clientAddress)
    elif request == b"RENEW": #send a renew message to server
        recordFound = checkRecord(mac)
        if recordFound:
            recordFound.timestamp = getSixtyFromNow()
            recordFound.ack = True
            #server.sendto(("ACKKNOWLEDGE".encode(), recordFound.mac, recordFound.ip, recordFound.timestamp), clientAddress)
            message = f"ACKNOWLEDGE {recordFound.mac} {ip_addresses[ip_counter]} {recordFound.timestamp}"

            server.sendto(message.encode(), clientAddress)
        else:
            if checkAvailable() != -1:
                unoccupiedIP = ip_addresses[checkAvailable()]
                available[checkAvailable()] = True
            else:
                exp = checkExpired()
                if exp is not None:
                    unoccupiedIP = exp.ip
                    records.append(Record(mac, unoccupiedIP, getSixtyFromNow()))
                    records.remove(exp)                    
                    message = f"OFFER {recordFound.mac} {recordFound.ip} {recordFound.timestamp}"
                    server.sendto(message.encode(), clientAddress)
                else:
                    server.sendto("DECLINE".encode(), clientAddress)






# Start a UDP server
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Avoid TIME_WAIT socket lock [DO NOT REMOVE]
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("", 9000)) #open port and start listening
print("DHCP Server running...")

'''
server contains a list of ip addresses.
we assume the lease time in our application is 60 secounds.
identify the a client by its mac adress

step 1: store a list of clients' mac addresses and ip address of each clinet and a timestanpt indicating the
time the uup addres will eb expired

When the server program receives a DISCOVER message:


'''

try:
    ip_counter= 0
    while True:
        server.settimeout(1)
        try:
            message, clientAddress = server.recvfrom(4096)#stuck here
        except socket.timeout:  
            continue
        
        
        request, mac, ip, timestamp = parse_message(message)#call parse message to split into request and mac 
        dhcp_operation(ip_counter, request, mac, clientAddress, ip)
        if request == b"DISCOVER":
            ip_counter += 1
        if request == b"LIST":
            server.sendto("EMPTY".encode(), clientAddress)
        elif request != None:
            server.sendto(request, clientAddress)
except OSError:
    print("os error")
    server.close()
except KeyboardInterrupt:
    print("Server closed")
    server.close()

server.close()
