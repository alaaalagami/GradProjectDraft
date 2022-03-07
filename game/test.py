#!/usr/bin/env python

from multiprocessing.connection import Client
import sys

message = sys.argv[1]
address = ('localhost', 6000)
conn = Client(address, authkey=b'momo')
conn.send(message)
conn.close()