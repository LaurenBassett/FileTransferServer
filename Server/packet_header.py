from datetime import datetime
from Cryptodome import Random
from Cryptodome.Cipher import AES
import os
import os.path
from os import listdir
from os.path import isfile, join
import time


class AS_REQ:
    def __init__ (self):
        self.type = "AS_REQ"
        self.client_ID = ""
        self.server_ID = ""
        self.time = datetime.now()
        self.encrypted = ""
class Credential:
    def __init__(self):
        self.ssc_key = ""
        self.server_ID = ""
        self.time = 0
        self.lifetime = 3600
        self.ticket_length = 0
        self.encrypted_ticket = ""

class AS_RESP:
    def __init__(self):
        self.type = ""
        self.cred_length = 0
        self.cred = self.Credential()


class Ticket: 
    def __init__ (self):
        self.ssc_key = ""
        self.client_ID = ""
        self.server_ID = ""
        self.time = datetime.now()
        self.size = 0
        self.lifetime = 36000
        self.expires_at= ""

class ap_request:
    def __init__(self):
        self.type = "AP_REQ"
        self.ticket_length = 0
        self.encrypted_ticket = ""
        self.client_ID = ""

class Encryptr:
    def __init__(self, key):
        self.key = key

    def pad(self,s):
        return s + b"\0" * (AES.block_size - len(s) % AES.block_size)

    def encrypt(self, message, key, key_size=256):
        message = self.pad(message)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return iv + cipher.encrypt(message)

    def decrypt(self, ciphertext, key):
        iv = ciphertext[:AES.block_size]
        cipher = AES.new((key.encode('utf-8')), AES.MODE_CBC, (iv.endcode('utf-8')))
        plaintext = cipher.decrypt(ciphertext[AES.block_size:])
        return plaintext.rstrip(b"\0")

    def encrypt_file(self, file_name):
        with open(file_name, 'rb') as fo:
            plaintext = fo.read()
        enc = self.encrypt(plaintext, self.key)
        with open(file_name + ".enc", 'wb') as fo:
            fo.write(enc)

    def decrypt_file(self, file_name, key):
        with open(file_name, 'rb') as fo:
            ciphertext = fo.read()
        dec = self.decrypt(ciphertext, key)
        with open(file_name[:-4], 'wb') as fo:
            fo.write(dec)

