import asyncio
from websockets.sync.client import connect
from websockets.server import serve

drive_control = connect("ws://localhost:8765")