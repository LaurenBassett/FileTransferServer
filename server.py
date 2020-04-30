import socket
import sys
import os
import pathlib
import time 
#AF_INET -> IPv4
#SOCK_STREAM -> TCP
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(), 1234))
s.listen(5) #queue
statistics = open("ServerStats.txt", "a+")
while True: 
    clientsocket, address = s.accept() #happy to see you 
    print(f"Connection from {address} has been established.\n")
    clientsocket.send(bytes("You may now access files on the server.", "utf-8"))
   # print("The time we connected to the server is %s" %tm.decode('ascii'))
    #lets send a file bro
    msg = clientsocket.recv(1024)
    command = msg.decode("utf-8")
  
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
    clientsocket.close()
    statistics.close()
    s.close()
    print("Goodbye!")
    quit()


s.close()

