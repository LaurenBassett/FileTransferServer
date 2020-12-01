import socket
import sys
import os
import pathlib
import time 
import pickle
from datetime import datetime
import pyAesCrypt
import packet_header as ph
from os import stat, remove
#AF_INET -> IPv4
#SOCK_STREAM -> TCP
class ap_request:
    def __init__(self):
        self.type = "AP_REQ"
        self.ticket_length = 0
        self.encrypted_ticket = ""
        self.client_ID = ""

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(), 1234))
s.listen(5) #queue
statistics = open("ServerStats.txt", "a+")
server_id_self = "bob"
ssc = open('ssc.txt', 'r')
secretSharedKey = ssc.read()
flagquit = False

clientsocket, address = s.accept() #happy to see you 
print(f"Recieved connection from {address}. Verifying credentials.\n")
clientsocket.send(bytes("Verifying credential...", "utf-8"))

# print("The time we connected to the server is %s" %tm.decode('ascii'))
#lets send a file bro
message = clientsocket.recv(1024)
server_ticket = pickle.loads(message)


size = stat("ticket.txt.aes").st_size
client = "alice"
#type
#ticket_length
#encrypted ticket
#clientID
bufferSize = 64 * 1024
password = secretSharedKey
with open("ticket.txt", "wb") as fOut:
    with open('ticket.txt.aes', "rb") as fIn:
        try:
            pyAesCrypt.decryptStream(fIn, fOut, secretSharedKey,bufferSize, size)
        except: 
            flagquit = True
           
fOut.close()
dT= open("ticket.txt", 'r')
decryptedTicket = dT.read()
delivered_SSC = decryptedTicket[0:32]
delivered_Client = decryptedTicket[32:37]
print(delivered_Client) 

#TODO:Check make sure server and client are good 
if flagquit == True:
    print("Client not authenticated.")
    clientsocket.send(bytes("-1", 'utf-8'))

    clientsocket.close()
    statistics.close()
    s.close()
    print("Goodbye!")
    quit()

if delivered_Client != client:
    print("Client not authenticated.")
    clientsocket.send(bytes("-1", 'utf-8'))
    clientsocket.close()
    statistics.close()
    s.close()
    print("Goodbye!")
    quit()
'''if server_ticket.time < server_ticket.expires_at:
    print("Client not authenticated.")
    clientsocket.close()
    statistics.close()
    s.close()
    print("Goodbye!")
    quit()'''

now = datetime.now()
print("Recieved connection from client at ",now )
clientsocket.send(bytes("Connection successful! You are authenticated.", 'utf-8'))
while True:  
    com = clientsocket.recv(1024)
    command = com[:].decode('utf-8')
  
    while (command !="-1"): 
        if (command == "1"):
            nm = clientsocket.recv(1024)
            filename = nm.decode("utf-8")
            if(filename != "-2"):
                print(f"File: {filename}")
                #recieve file
                statistics.write("Upload recieved at %d\n" %int(round(time.time() * 1000)))
                f = open(filename, "wb")
                #filesize = os.path.getsize(filename)
                file_data = clientsocket.recv(1024)
                f.write(file_data)       
                f.close()
                size = os.stat(filename).st_size
                print("file has been uploaded successfully.")
                statistics.write("->Upload resolved at %d\n" %int(round(time.time() * 1000)))
                statistics.write("Size of file: %d MB\n\n" %size)
            else:
                print("Error: File not found.")
        elif (command == "2"):
            #download file
            nm = clientsocket.recv(1024)
            filename = nm[:].decode("utf-8")
            print(f"File: {filename}")
            file_location = pathlib.Path(filename)
            if file_location.exists():
                statistics.write("Download started at %d\n" %int(round(time.time() * 1000)))
                clientsocket.send(bytes("y",'utf-8'))
                f = open(filename, "rb")
                file_data = f.read(1024)
                clientsocket.send(file_data)
                f.close()
                size = os.stat(filename).st_size
                print("File has been downloaded successfully")
                statistics.write("->Download resolved at %d\n" %int(round(time.time() * 1000)))
                statistics.write("Size of file: %d MB\n\n" %size)
            else: 
                clientsocket.send(bytes("n",'utf-8'))

        elif (command == "3"):
            nm = clientsocket.recv(1024)
            filename = nm[:].decode("utf-8")
            if (filename == "-1"):
                print("Local Delete, no action needed.")
            else: 
                print(f"File: {filename}")
                file_location= pathlib.Path(filename)
                if file_location.exists():
                    statistics.write("Delete request recieved at %d\n" %int(round(time.time() * 1000)))
                    size = os.stat(filename).st_size
                    os.remove(filename)
                    clientsocket.send(bytes("File has successfully been deleted", 'utf-8'))
                    statistics.write("->Deletion completed at %d\n" %int(round(time.time() * 1000)))
                    statistics.write("Size of file: %d MB\n\n" %size)
                else: 
                    clientsocket.send(bytes("The file does not exist", 'utf-8'))
            
        elif (command == '4'):
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
        print("Ready for your next input..")
        msg = clientsocket.recv(1024)
        command = msg.decode("utf-8")
        if command == "":
            print("Looks like client may have disconnected, please reconnect.")
            quit()
      
    clientsocket.close()
    statistics.close()
    s.close()
    print("Goodbye!")
    quit()


s.close()

