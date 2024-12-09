import json
from dotenv import dotenv_values
from websockets.sync.client import connect
from websockets.server import serve

from stream import RtspManager

config = dotenv_values("config.env")
DRIVE_CONTROL_IP = config["DRIVE_CONTROL_IP"]
DRIVE_CONTROL_PORT = int(config["DRIVE_CONTROL_PORT"])
SERVE_IP = config["SERVE_IP"]
SERVE_PORT = int(config["SERVE_PORT"])
CAR_ID = config["CAR_ID"]

RTSP_OPTIONS = {
    "device_id": int(config["CAM_DEVICE_ID"]),
    "fps": int(config["FPS"]),
    "image_width": int(config["IMAGE_WIDTH"]),
    "image_height": int(config["IMAGE_HEIGHT"]),
    "port": SERVE_PORT
}

drive_control = connect(f"ws://{DRIVE_CONTROL_IP}:{DRIVE_CONTROL_PORT}")
rtsp_manager = RtspManager()

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
            rtsp_manager.start()
        elif message_type == "stop_video":
            rtsp_manager.stop()
        else:
            await websocket.send(json.dumps({"type": "error", "message": "Invalid message type"}))
            
async def main():
    async with serve(handle_message, SERVE_IP, SERVE_PORT) as server:
        await server.serve_forever()