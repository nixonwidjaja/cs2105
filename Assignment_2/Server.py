#!/usr/bin/env python3
import sys

from ServerClientRelease import ServerClient

server_client = ServerClient(sys.argv, is_server=True)
# receive files
server_client.send_file()
server_client.terminate()
