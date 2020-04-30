import socket
import timeit
import sys
import pathlib
import os
import glob 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), 1234)) #now we are going to connect to the server locally. 

msg = s.recv(1024)
print(msg.decode("utf-8"))

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
    command = str(input("Would you like to process another file?\nUpload[1], Download[2], Delete[3]\n or type -1 to quit\n>>"))

s.send(bytes(command, 'utf-8'))
print("All done!")
s.close()
