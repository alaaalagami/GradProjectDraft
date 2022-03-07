#!/usr/bin/env python

import asyncio
import websockets
from multiprocessing.connection import Listener, Client
import enum
import json

# This is the state of the client relative to RenPy
class State(enum.Enum):
   Idle = 0
   Listen = 1
   Send = 2

async def create_webclient(uri, renpy_address):
    webclient = WebClient(uri, renpy_address)
    await webclient._connect()
    return webclient

class WebClient():

    def __init__(self, uri, renpy_address):
        self.uri = uri
        self.to_renpy_address = renpy_address
        self.from_renpy_address = (renpy_address[0], renpy_address[1]+2000)
        self.websocket = None
        self.state = State.Send
    
    async def _connect(self):
        self.websocket = await websockets.connect(self.uri)
        print("connected")

    async def send_to_server(self, message):
        await self.websocket.send(message)

    async def recv_from_server(self):
        message = await self.websocket.recv()
        return message
    
    def send_to_renpy(self, message):
        renpy_client = Client(self.to_renpy_address, authkey=b'momo')
        renpy_client.send(message)
        renpy_client.close()

    def recv_from_renpy(self):
        renpy_listener = Listener(self.from_renpy_address, authkey=b'momo')
        conn = renpy_listener.accept()
        message = conn.recv()
        conn.close()
        return message
    
    async def close(self):
        await self.websocket.close()
    
    def get_state(self):
        return self.state
    
    def make_idle(self):
        self.state = State.Idle
    
    async def first_player_login(self):
        init = self.recv_from_renpy()
        assert init == 'host'
        event = {"type": "init"}
        await self.send_to_server(json.dumps(event))
        join_key = json.loads(await self.recv_from_server())
        print(join_key)
        self.send_to_renpy(join_key['join'])


async def main():
    renpy_address = ('localhost', 5000)
    uri = "ws://localhost:8765"  # "wss://testing-multiplayer-gradproj.herokuapp.com"
    myclient = await create_webclient(uri, renpy_address)
    print('lets login player 1')
    await myclient.first_player_login()
    print('logged in player 1')

#    while True:
#        current_state = myclient.get_state()
#        if current_state == State.Listen:
#            message = myclient.recv_from_renpy()
#            await myclient.send_to_server(message)
#
#        elif current_state == State.Send:
#            message = await myclient.recv_message()
#            myclient.send_to_renpy(message)
#


asyncio.run(main())