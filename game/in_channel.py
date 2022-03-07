#!/usr/bin/env python

from multiprocessing.connection import Listener

address = ('localhost', 5000)
listener = Listener(address, authkey=b'momo')
conn = listener.accept()
message = conn.recv()
conn.close()
print(message)