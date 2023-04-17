# !/usr/bin/env python3
import os
import sys
from Cryptodome.Hash import SHA256

if len(sys.argv) < 3:
    print("Usage: python3 ", os.path.basename(__file__), "key_file_name document_file_name")
    sys.exit()

key_file_name   = sys.argv[1]
file_name       = sys.argv[2]

# get the authentication key from the file
# TODO
key_file = open(key_file_name, 'rb')
key = key_file.read()
# read the input file
file = open(file_name, 'rb')
# First 32 bytes is the message authentication code
# TODO
data = file.read()
mac_from_file = data[:32]
data_rest = data[32:] + key
# Use the remaining file content to generate the message authentication code
# TODO
mac_generated = SHA256.new(data_rest).digest()
if mac_from_file == mac_generated:
    print ('yes')
else:
    print ('no')
