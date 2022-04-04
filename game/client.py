#!/usr/bin/env python

import asyncio
import websockets
import socket
import json
import os
import sys


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

    
    async def _connect(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(self.renpy_address)
        s.listen()
        self.renpy_socket, _ = s.accept()
        print("connected to renpy")
        self.websocket = await websockets.connect(self.uri, ping_interval = None)
        print("connected to web server")
        

    async def send_to_server(self, message):
        print("Sent", message)
        await self.websocket.send(json.dumps(message))

    async def recv_from_server(self):
        message = await self.websocket.recv()
        print("Received", message)
        return json.loads(message)
    
    def send_to_renpy(self, message):
        self.renpy_socket.sendall(message.encode('utf-8'))

    def recv_from_renpy(self):
        message = self.renpy_socket.recv(4096)
        return message.decode('utf-8')
  
    async def close(self):
        self.renpy_socket.close()
        await self.websocket.close()
    
    
    async def player_login(self):
        init = self.recv_from_renpy()

        if init == 'host':
            print('lets login player 1')
            event = {"type": "init"}
            await self.send_to_server(event)
            join_key = await self.recv_from_server()
            self.send_to_renpy(join_key['join'])
            await self.recv_from_server()
            self.send_to_renpy('joined')

        elif init == 'join':
            print('lets login player 2')
            key = self.recv_from_renpy()
            event = {"type": "join", "key": key}
            await self.send_to_server(event)
            await self.recv_from_server()
            self.send_to_renpy('joined')


        else:
            raise ValueError()
    
    async def pick_role(self):
        role = self.recv_from_renpy()
        event = {'type': 'role', 'pick': role}
        await self.send_to_server(event)
    
    async def get_first_scene(self):
        first_scene = await self.recv_from_server()
        self.send_to_renpy(first_scene['label'])


async def main():
    port = int(sys.argv[1])
    renpy_address = ('localhost', port)
    uri = "ws://localhost:8765" #"wss://experience-manager-grad-proj.herokuapp.com/" 
    myclient = await create_webclient(uri, renpy_address)

    await myclient.player_login()

    await myclient.pick_role()

    await myclient.get_first_scene()

    while True:
        request = json.loads(myclient.recv_from_renpy())
        type = request['type']

        if type == 'choice':
            await myclient.send_to_server(request)

        elif type == 'show_request':
            await myclient.send_to_server(request)
            next_scene = await myclient.recv_from_server()
            myclient.send_to_renpy(next_scene['label'])
            if next_scene['label'] == 'end_scene':
                break

    await myclient.close()


asyncio.run(main())