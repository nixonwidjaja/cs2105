#!/usr/bin/env python3
import sys

from ServerClientRelease import ServerClient

server_client = ServerClient(sys.argv, is_server=False)
# receive files
server_client.recv_file()
server_client.terminate()
