#!/usr/bin/env python

import asyncio
import websockets
from multiprocessing.connection import Listener, Client
import enum

renpy_address = ('localhost', 6000)

async def create_webclient(uri):
    client = WebClient(uri)
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
        self.state = State.Send
    
    async def _connect(self):
        self.websocket = await websockets.connect(self.uri)
        print("connected")

    async def send_message(self, message):
        await self._connect()
        await self.websocket.send(message)
        await self.recv_message()

    async def recv_message(self):
        await self._connect()
        message = await self.websocket.recv()
        print('received', message)
        return message
    
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
            renpy_listener = Listener(renpy_address, authkey=b'momo')
            conn = renpy_listener.accept()
            print('connection accepted from', renpy_listener.last_accepted)
            msg = conn.recv()
            await myclient.send_message(msg)
            conn.close()
            await myclient.close()

        elif current_state == State.Send:
            renpy_client = Client(renpy_address, authkey=b'momo')
            message = await myclient.recv_message()
            renpy_client.send(message)
            renpy_client.close()
            await myclient.close()
            





    

asyncio.run(main())