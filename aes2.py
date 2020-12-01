import pyAesCrypt
from os import stat, remove
# encryption/decryption buffer size
bufferSize = 64 * 1024
fssc = open("ssc.txt", 'r')

password = fssc.read()# encryption of file data.txt
with open("ticket.txt", "rb") as fIn:
    with open("ticket.txt.aes", "wb") as fOut:
        pyAesCrypt.encryptStream(fIn, fOut, password, bufferSize)# get encrypted file size
encFileSize = stat("ticket.txt.aes").st_size
print(encFileSize) #prints file size# decryption of file data.aeswith open("data.txt.aes", "rb") as fIn:
with open("dataout.txt", "wb") as fOut:
    try:
    # decrypt file stream
        pyAesCrypt.decryptStream(fIn, fOut, password, bufferSize, encFileSize)
    except ValueError:
    # remove output file on error
        remove("dataout.txt")