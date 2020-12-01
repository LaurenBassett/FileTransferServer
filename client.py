import socket
import timeit
import sys
import pathlib
import os
import glob 
import pickle
import hashlib
import packet_header
import time
from datetime import datetime
from os import stat, remove
import pyAesCrypt
import time
from os import stat, remove
#TODO: Connect to Authentication Server 
'''
Client sends request to Authentication Server
Gets an encrypted credential. 
Decrypts the credential using the client key
Sends packet to server'''


#-----------------------------------------AUTH-SERVER-------------------------------------#
a = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    a.connect((socket.gethostname(), 4321))
except:
    print("Authentication server is not online!")
    quit()
msg = a.recv(1024)
print(msg.decode("utf-8"))

#Send user ID and secret key


#Connection has been established, send ticket
authReq = packet_header.AS_REQ()
authReq.client_ID = input("enter client id: ")
client_key =input("enter client key: ")
print()
authReq.server_ID = input("enter server id: ")
authReq.type = "AS_REQ"

L = [authReq.client_ID, authReq.server_ID]
request_message = open("apreq.txt", 'w')
request_message.writelines(L)
request_message.close()
bufferSize = 64*1024
password = client_key
with open("apreq.txt", "rb") as f_ticket:
    with open("apreq.txt.aes", 'wb') as f_encrypted_ticket:
        pyAesCrypt.encryptStream(f_ticket, f_encrypted_ticket, password, bufferSize)
size = stat("apreq.txt.aes").st_size
f_ticket.close()
f_encrypted_ticket.close()
authReq.encrypted = "apreq.txt.aes"
ticket_packet = pickle.dumps(authReq)
a.send(ticket_packet)
auth_msg = a.recv(1024)
print(auth_msg.decode("utf-8"))

authCred = a.recv(1024)
authResp = pickle.loads(authCred)
if authResp.type == "-1":
    print("Credentials not accepted. Goodbye.")
    quit()
creds = packet_header.Credential 
creds = authResp.cred

a.close()
#----------------------------------------------SERVER-------------------------------------#

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect((socket.gethostname(), 1234)) #now we are going to connect to the server locally. 
except:
    print("Server is not online.")
    quit()

msg = s.recv(1024)
print(msg.decode("utf-8"))
#Message recieved. Send credential. 
#decrypt credential 
filename = creds.encrypted_ticket
size = creds.ticket_length
SecretSharedKey = creds.ssc_key
Server = creds.server_ID
timer = creds.time
timeout = timer + 36000

#-------Request Packet to Server------#
server_request = packet_header.ap_request
server_request.ticket_length = size 
server_request.encrypted_ticket = filename
server_request.client_ID = authReq.client_ID

ticket_to_send = pickle.dumps(server_request)

s.send(ticket_to_send)
auth_response = s.recv(1024)
check = auth_response[:].decode("utf-8")
if check == "-1":
    print("Unable to authenticate. Goodbye.")
    quit()

#s.send(bytes("Client sucessfully authenticated. Connection to server established. ", 'utf-8'))
command = str(input("Would you like to:\nUpload [1]\nDownload [2]\nDelete [3]?\nSee All Files [4]\nHit enter -1 to quit. \n >>"))
while (command != "-1"):

    s.send(bytes(command, 'utf-8'))
    
    if (command == '1'):
        filename = str(input("What is your filename? \t >>"))
        file_location = pathlib.Path(filename)
        if file_location.exists():
            s.send(bytes(filename, "utf-8"))
            f = open(filename, "rb")
            file_data = f.read(1024)
            s.send(file_data)
        else: 
            print("Sorry, file does not exist.")
            s.send(bytes("-2", "utf-8"))
    elif (command == '2'):
        filename = str(input("What is your filename? \t >>"))
        #download
        s.send(bytes(filename,"utf-8"))
        flag = s.recv(1024)
        flag = flag.decode('utf-8')
        if (flag == "y"):
            f = open(filename, "wb")
            file_data = s.recv(1024)
            f.write(file_data)       
            f.close()
        else:
            print("Sorry, file does not exist.")
    elif (command == '3'):
        ask = str(input("Are you deleting on client or server?\n Client [1]\n Server [2]\n>>"))
        if (ask == '1'): 
            filename = str(input("What is your filename? \t >>"))
            file_location = pathlib.Path(filename)
            s.send(bytes("-1", "utf-8"))
            if file_location.exists():
                os.remove(filename)
                print("File deleted successfully")
            else:
                print("File does not exist.")
        elif (ask == '2'):
            filename = str(input("What is your filename? \t >>"))
            s.send(bytes(filename,"utf-8"))
            response = s.recv(1024)
            print(response.decode('utf-8'))
        else:
            print("Not a valid input.")
    elif (command == '4'):
        #print directory
        statfile = open("fileStats.txt", "a+")
        statfile.write("____________________________")

        for p in pathlib.Path('.').iterdir():
            if p.is_file():
                size = os.stat(p).st_size
                print(f"The file {p} is {size} MB")
                statfile.write("\n")
                statfile.write("File: %s\n" %p)
                statfile.write("File Size: %d MB\n" %size)
                statfile.write("File was last accessed on: %d \n" %os.stat(p).st_atime)
        statfile.close()

    else:
        print("Did not recognize input")
    
    print("The time is: ", datetime.now())
    current_time = int(round(time.time() * 1000))
    percent_left = (current_time/timeout) * 100
    if (current_time > timeout):
        print("Server has timed out. Please reauthenticate.")
        s.send(bytes("-1", 'utf-8'))
        quit()
    else:
       # print("You have used ", percent_left,"% of your time.\n\n" )
        command = str(input("Would you like to process another file?\nUpload[1], Download[2], Delete[3]\n or type -1 to quit\n>>"))

s.send(bytes(command, 'utf-8'))
print("All done!")
s.close()
