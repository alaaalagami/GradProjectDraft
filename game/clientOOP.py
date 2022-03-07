#!/usr/bin/env python

import asyncio
import websockets
from multiprocessing.connection import Listener, Client
import enum

from_renpy_address = ('localhost', 6000)
to_renpy_address = ('localhost', 5000)
renpy_listener = Listener(from_renpy_address, authkey=b'momo')
#renpy_client = Client(to_renpy_address, authkey=b'momo')

async def create_webclient(uri):
    client = WebClient(uri)
    await client._connect()
    return client

# This is the state of the client relative to RenPy
class State(enum.Enum):
   Idle = 0
   Listen = 1
   Send = 2

class WebClient():

    def __init__(self, uri):
        self.uri = uri
        self.websocket = None
        self.state = State.Listen
    
    async def _connect(self):
        self.websocket = await websockets.connect(self.uri)
        print("connected")

    async def send_message(self, message):
        await self.websocket.send(message)
        await self.recv_message()
    
    async def recv_message(self):
        message = await self.websocket.recv()
        print('received', message)
    
    async def close(self):
        await self.websocket.close()
    
    def get_state(self):
        return self.state
    
    def make_idle(self):
        self.state = State.Idle

async def main():
    uri = "ws://localhost:8765"  # "wss://testing-multiplayer-gradproj.herokuapp.com"
    myclient = await create_webclient(uri)

    while True:
        current_state = myclient.get_state()
        if current_state == State.Listen:
            print(current_state)
            conn = renpy_listener.accept()
            print('connection accepted from', renpy_listener.last_accepted)
            msg = conn.recv()
            await myclient.send_message(msg)
            conn.close()
            myclient.make_idle()

        
    await myclient.close()

    renpy_listener.close()


asyncio.run(main())