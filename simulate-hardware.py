import json
import asyncio
from dotenv import dotenv_values
from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosedError

config = dotenv_values("config.env")
DRIVE_CONTROL_IP = config["DRIVE_CONTROL_IP"]
DRIVE_CONTROL_PORT = int(config["DRIVE_CONTROL_PORT"])

async def handle_message(websocket):
    try:
        async for message in websocket:
            message_data = json.loads(message)
            print(f"Angle: {message_data["angle"]} \tForward: {message_data["forward"]} \tAccelerate: {message_data["accelerate"]}")
    except ConnectionClosedError:
        print("Connection to command server closed unexpectedly.")

async def main():
    print("Starting server...")
    async with serve(handle_message, DRIVE_CONTROL_IP, DRIVE_CONTROL_PORT) as server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())