#!/usr/bin/env python

import asyncio
import websockets
import os
import signal
import json
import secrets

# async def echo(websocket):
#     async for message in websocket:
#         print('received', message)
#         await websocket.send("3ayz abosak")

JOIN = {}

async def error(websocket, message):
    """
    Send an error message.

    """
    event = {
        "type": "error",
        "message": message,
    }
    await websocket.send(json.dumps(event))


async def play(websocket, connected):
    """
    Receive and process moves from a player.

    """
    async for message in websocket:
        # Parse a "play" event from the UI.
        event = json.loads(message)
        assert event["type"] == "play"
        column = event["column"]

        try:
            # Play the move.
            row = game.play(player, column)
        except RuntimeError as exc:
            # Send an "error" event if the move was illegal.
            await error(websocket, str(exc))
            continue

        # Send a "play" event to update the UI.
        event = {
            "type": "play",
            "player": player,
            "column": column,
            "row": row,
        }
        websockets.broadcast(connected, json.dumps(event))

async def start(websocket):
    """
    Handle a connection from the first player: start a new game.

    """
    # Initialize a Connect Four game, the set of WebSocket connections
    # receiving moves from this game, and secret access tokens.
 #   game = Connect4()
    connected = {websocket}

    join_key = secrets.token_urlsafe(2)
    JOIN[join_key] = connected

    try:
        # Send the secret access tokens to the browser of the first player,
        # where they'll be used for building "join" and "watch" links.
        event = {
            "type": "init",
            "join": join_key,
        }
        await websocket.send(json.dumps(event))
        # Receive and process moves from the first player.
        await play(websocket, connected)
    finally:
        del JOIN[join_key]


async def join(websocket, join_key):
    """
    Handle a connection from the second player: join an existing game.

    """
    # Find the Connect Four game.
    try:
        game, connected = JOIN[join_key]
    except KeyError:
        await error(websocket, "Game not found.")
        return

    # Register to receive moves from this game.
    connected.add(websocket)
    try:
        # Send the first move, in case the first player already played it.
        pass
#        await replay(websocket, game)
        # Receive and process moves from the second player.
#        await play(websocket, game, PLAYER2, connected)
    finally:
        connected.remove(websocket)


async def handler(websocket, path):
    """
    Handle a connection and dispatch it according to who is connecting.

    """
    # Receive and parse the "init" event from the host.
    message = await websocket.recv()
    event = json.loads(message)
    assert event["type"] == "init"

    if "join" in event:
        # Second player joins an existing game.
        await join(websocket, event["join"])
    else:
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