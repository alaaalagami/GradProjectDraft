#!/usr/bin/env python

import asyncio
import websockets
import os
import signal
import json
import random
import string
import ast
from experience_manager import ExperienceManager

JOIN = {}

async def start(websocket):
    # Initialize an Experience Manager, the set of WebSocket connections
    # receiving events from this game, and secret access token.
    game = ExperienceManager()
    connected = {websocket}

    join_key = "".join(random.choice(string.ascii_letters) for _ in range(4))

    JOIN[join_key] = game, connected

    try:
        # Send the secret access token to the client of the first player.
        event = {
            "type": "init",
            "join": join_key,
        }
        await websocket.send(json.dumps(event))

        # Temporary - for testing.
        print("first player started game", id(game))
        async for message in websocket:
            print("first player sent", message)

    finally:
        del JOIN[join_key]


async def handler(websocket):
    # Receive and parse the "init" event from the Client
    message = await websocket.recv()
    print(message)
    event = json.loads(message)
    assert event["type"] == "init"
    print('received init')

    # First player starts a new game.
    await start(websocket)

async def main():
    # Set the stop condition when receiving SIGTERM.
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    port = int(os.environ.get("PORT", "8765"))
    async with websockets.serve(handler, "", port):
        await stop


asyncio.run(main())