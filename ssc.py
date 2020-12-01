#Generate Random Secret Shared Key and Export to File for Client/Server to Read In
'''This program generates a random 36 bit secret shared key that is used with the client/server program. 
This key should be generated at the end of the session to establish the key for the next session, and then encrypted.'''

import random as r 

def main():
    key = ''
    allowed_chars="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    for i in range (0,32):
        if i % 32 == 0 and i != 0:
            key +='-'

        key += str(allowed_chars[r.randint(0, len(allowed_chars) - 1)])

    f = open("Server/ssc.txt", 'w')

    f.write(key)
    f.close()

    f = open("ssc.txt", 'w')
    f.write(key)
    f.close()
main()
