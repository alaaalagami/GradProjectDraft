#!/usr/bin/env python

import asyncio
import websockets
import json

uri = "ws://localhost:8765"
choice_file_contents = None

def new_choice_available():
    global choice_file_contents
    with open('info/choice.txt', 'r') as choice_file:
        new_contents = choice_file.readlines()
        if choice_file_contents != new_contents:
            choice_file_contents = new_contents
            return True
        else:
            return False

async def main():
    async with websockets.connect(uri) as websocket:
        event = {'type': 'init'}
        await websocket.send(json.dumps(event))

        while True:
            if new_choice_available() and len(choice_file_contents) != 0:
                event = {'type': 'choice', 'content': choice_file_contents}
                await websocket.send(json.dumps(event))

            response = await websocket.recv()
            response = json.loads(response)
            print(response)
            if response['type'] == 'init':
                join_key = response['join']
                with open('info/join_key.txt', 'w') as join_file:
                    join_file.write(join_key)
            elif response['type'] == 'scene':
                with open('info/next_scene.txt') as next_scene:
                    next_scene.write(response['label'])


asyncio.run(main())