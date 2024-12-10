import json
import asyncio
from dotenv import dotenv_values
from websockets.sync.client import connect
from websockets.server import serve
from subprocess import Popen
import signal

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

config = dotenv_values("config.env")
DRIVE_CONTROL_IP = config["DRIVE_CONTROL_IP"]
DRIVE_CONTROL_PORT = int(config["DRIVE_CONTROL_PORT"])
SERVE_IP = config["SERVE_IP"]
SERVE_PORT = int(config["SERVE_PORT"])
CAR_ID = config["CAR_ID"]

RTSP_OPTIONS = {
    "device_id": config["CAM_DEVICE_ID"],
    "fps": config["FPS"],
    "image_width": config["IMAGE_WIDTH"],
    "image_height": config["IMAGE_HEIGHT"],
    "port": config["VIDEO_PORT"]
}

drive_control = connect(f"ws://{DRIVE_CONTROL_IP}:{DRIVE_CONTROL_PORT}")

async def handle_message(websocket):
    global rtsp_process

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
        else:
            await websocket.send(json.dumps({"type": "error", "message": "Invalid message type"}))
            
async def main():
    Popen(['python3', 'stream.py', 
            '--device_id', RTSP_OPTIONS["device_id"], 
            '--fps', RTSP_OPTIONS["fps"], 
            '--image_width', RTSP_OPTIONS["image_width"], 
            '--image_height', RTSP_OPTIONS["image_height"], 
            '--port', RTSP_OPTIONS["port"]])
    async with serve(handle_message, SERVE_IP, SERVE_PORT) as server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())