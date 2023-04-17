import os.path
import sys
from socket import *
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_v1_5, AES

rsa_key_len = int(2048/8)


def load_rsa_key(f_name_key="test/rsa_key.bin"):
    """
    load the public RSA key
    :return: RSA key
    """
    # TODO
    f = open(f_name_key, 'r')
    arr = f.read()
    return RSA.import_key(arr)


# connect ot the server
if len(sys.argv) < 5:
    print ("Usage: python3 ", os.path.basename(__file__), "key_file_name data_file_name hostname/IP port")
else:
    key_file_name   = sys.argv[1]
    data_file_name  = sys.argv[2]
    serverName      = sys.argv[3]
    serverPort      = int(sys.argv[4])
    print (serverName, serverPort)

    rsa_key     = load_rsa_key()

    # connect to the server
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))

    # get the session key
    # first 256 bytes sent by the server is the RSA encrypted session key
    cipher_rsa = PKCS1_v1_5.new(rsa_key)
    # TODO
    ciphertext = clientSocket.recv(256)
    session_key = cipher_rsa.decrypt(ciphertext=ciphertext, sentinel=b'')

    # write the session key to the file "key_file_name"
    # TODO
    with open(key_file_name, 'wb') as f:
        f.write(session_key)
    # get the data and write to file "data_file_name"
    cipher_aes = AES.new(session_key, AES.MODE_ECB)

    # get the data from server
    # TODO
    # decrypt the data in blocks of size 16B
    # size of data from the server is guaranteed to be a multiple of 16B
    # TODO
    with open(data_file_name, 'wb') as f:
        while True:
            try:
                data = clientSocket.recv(16)
                if len(data) == 0:
                    break
                f.write(cipher_aes.decrypt(data))
            except:
                break
    clientSocket.close()

