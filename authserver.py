import socket
import timeit
import sys
import pathlib
import os
import os.path
import glob 
import pickle
import packet_header as ph
from Cryptodome.Cipher import AES
import random as r 
import pyAesCrypt
import time
from os import stat, remove
# encryption/decryption buffer size

a = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
a.bind((socket.gethostname(), 4321))
a.listen(5) #queue

while True: 
    clientsocket, address = a.accept() #happy to see you 
    print(f"Connection from {address} has been established.\n")
    bufferSize = 64*1024
    clientsocket.send(bytes("Waiting on Client to Authenticate...\n", "utf-8"))
    password = "abc"
    msg = clientsocket.recv(1024)
    size = stat("apreq.txt.aes").st_size
    ticket_var = pickle.loads(msg)
    with open("apreq.txt", "wb") as fOut:
        with open('apreq.txt.aes', "rb") as fIn:
            pyAesCrypt.decryptStream(fIn, fOut, password ,bufferSize, size)
           
    fOut.close()
    dT= open("apreq.txt", 'r')
    decryptedreq = dT.read()
    delivered_Client= decryptedreq[0:5]

    print(delivered_Client) 

    print("Ticket generated at ", ticket_var.time)
    time_in_digits = int(round(time.time() * 1000))

    #authentication process:
    if delivered_Client != "alice":
        clientsocket.send(bytes("Failed to Identify Client.", "utf-8"))
        #response packet to leave
        fail = ph.AS_RESP()
        fail.type = "-1"
        fail.cred = "-1"
        fail.cred_length = "-1"
        respond = pickle.dumps(fail)
        clientsocket.send(respond)
        a.close()
    clientsocket.send(bytes("Client identified. Generating credentials now.", "utf-8"))
    f_ticket = open("ticket.txt", 'w')
    
    #Generating ticket for the server
    ssc = open("ssc.txt", 'r')
    ticket = ph.Ticket()
    ticket.ssc_key = ssc.read()
    ticket.client_ID = ticket_var.client_ID
    ticket.server_ID = ticket_var.server_ID
    
    L = [ticket.ssc_key, ticket.client_ID, ticket.server_ID]
    f_ticket.writelines(L) 
    f_ticket.close()
    bufferSize = 64 * 1024
    password = ticket.ssc_key
    with open("ticket.txt", "rb") as f_ticket:
        with open("Server/ticket.txt.aes", 'wb') as f_encrypted_ticket:
            pyAesCrypt.encryptStream(f_ticket, f_encrypted_ticket, password, bufferSize)
    ticket.size = stat("ticket.txt.aes").st_size
    f_ticket.close()
    f_encrypted_ticket.close()
    #f_cred = encrcred.read()
    
    cred = ph.Credential()
    cred.ssc_key = ssc.read()
    cred.server_ID = ticket_var.server_ID
    cred.time = time_in_digits
    cred.ticket_length = ticket.size
    cred.encrypted_ticket = "ticket.txt.aes"
    #TODO: enrypted ticket 
   
   #
    #Send credential back to client: 
    asresp = ph.AS_RESP()
    asresp.type = "AS_RESP"
    asresp.ticket_length = cred.ticket_length
    asresp.cred = cred 
    
    asresp.cred_length = 64
    # 
    respond = pickle.dumps(asresp)
    clientsocket.send(respond)  

    clientsocket.close()
    a.close()
    print("Goodbye!")
    quit()


a.close()

