#!/usr/bin/env python

import asyncio
import websockets
# from multiprocessing.connection import Listener, Client
import socket
import enum
import json
import os

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
        self.renpy_socket = None
        self.renpy_address = renpy_address
        self.websocket = None
        self.state = State.Send

    
    async def _connect(self):
        os.system('fuser -k 5000/tcp')
        self.websocket = await websockets.connect(self.uri)
        print("connected to web server")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(self.renpy_address)
        s.listen()
        self.renpy_socket, _ = s.accept()
        print("connected to renpy")
        

    async def send_to_server(self, message):
        await self.websocket.send(message)

    async def recv_from_server(self):
        message = await self.websocket.recv()
        return message
    
    def send_to_renpy(self, message):
        self.renpy_socket.sendall(message.encode('utf-8'))

    def recv_from_renpy(self):
        message = self.renpy_socket.recv(1024)
        return message.decode('utf-8')
    
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
    await myclient.close()

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