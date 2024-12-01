import json
from dotenv import dotenv_values
from websockets.sync.client import connect
from websockets.server import serve

config = dotenv_values("config.env")
DRIVE_CONTROL_IP = config["DRIVE_CONTROL_IP"]
DRIVE_CONTROL_PORT = int(config["DRIVE_CONTROL_PORT"])
SERVE_IP = config["SERVE_IP"]
SERVE_PORT = int(config["SERVE_PORT"])
AGORA_APP_ID = config["AGORA_APP_ID"]

drive_control = connect(f"ws://{DRIVE_CONTROL_IP}:{DRIVE_CONTROL_PORT}")

async def handle_message(websocket):
    async for message in websocket:
        message_data = json.loads(message)
        message_type = message_data["type"]
        if message_type == "ping":
            await websocket.send(json.dumps({"type": "pong"}))
        elif message_type == "drive":
            await drive_control.send(json.dumps({
                "angle": message_data["angle"],
                "accelerate": message_data["accelerate"]
            }))
        elif message_type == "start_video":
            pass
        elif message_type == "stop_video":
            pass
        else:
            await websocket.send(json.dumps({"type": "error", "message": "Invalid message type"}))

async def start_video():
    pass
            
async def main():
    async with serve(handle_message, SERVE_IP, SERVE_PORT) as server:
        await server.serve_forever()