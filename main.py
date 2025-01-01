import json
import asyncio
from dotenv import dotenv_values
from websockets.asyncio.client import connect
from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosedError
from subprocess import Popen

config = dotenv_values("config.env")
DRIVE_CONTROL_IP = config["DRIVE_CONTROL_IP"]
DRIVE_CONTROL_PORT = int(config["DRIVE_CONTROL_PORT"])
SERVE_IP = config["SERVE_IP"]
SERVE_PORT = int(config["SERVE_PORT"])

PASSWORD = config["PASSWORD"]

RTSP_OPTIONS = {
    "device_id": config["CAM_DEVICE_ID"],
    "fps": config["FPS"],
    "image_width": config["IMAGE_WIDTH"],
    "image_height": config["IMAGE_HEIGHT"],
    "port": config["VIDEO_PORT"]
}

def generate_error_string(message):
    return json.dumps({"type": "error", "message": message})

def is_int(value):
    try:
        int(value)
    except ValueError:
        return False
    
    return True

def is_bool(value):
    return value is True or value is False

async def handle_message(websocket):
    try:
        async for message in websocket:
            try:
                message_data = json.loads(message)
                if "token" not in message_data:
                    await websocket.send(generate_error_string("Token not provided."))
                    continue

                if message_data["token"] != PASSWORD:
                    await websocket.send(generate_error_string("Invalid token provided."))
                    continue

                if "type" not in message_data:
                    await websocket.send(generate_error_string("Message type not provided."))
                    continue
                
                message_type = message_data["type"]
                if message_type == "ping":
                    await websocket.send(json.dumps({"type": "pong"}))
                elif message_type == "drive":
                    if "angle" not in message_data:
                        await websocket.send(generate_error_string("Angle not provided."))
                        continue
                    if "accelerate" not in message_data:
                        await websocket.send(generate_error_string("Accelerate (pedal pressed) not provided."))
                        continue

                    if not is_int(message_data["angle"]) or not (-90 <= message_data["angle"] <= 90):
                        await websocket.send(generate_error_string("Invalid angle provided."))
                        continue
                    if not is_int(message_data["accelerate"]) or not (-100 <= message_data["accelerate"] <= 100):
                        await websocket.send(generate_error_string("Invalid accelerate (pedal pressed) provided."))
                        continue

                    await drive_control.send(json.dumps({
                        "angle": message_data["angle"],
                        "accelerate": message_data["accelerate"]
                    }))
                else:
                    await websocket.send(generate_error_string("Invalid message type."))
            except:
                await websocket.send(generate_error_string("Failed to parse message."))
    except ConnectionClosedError:
        print("Connection to app closed unexpectedly.")

async def main():
    global drive_control
    Popen(['python3', 'stream.py', 
            '--device_id', RTSP_OPTIONS["device_id"], 
            '--fps', RTSP_OPTIONS["fps"], 
            '--image_width', RTSP_OPTIONS["image_width"], 
            '--image_height', RTSP_OPTIONS["image_height"], 
            '--port', RTSP_OPTIONS["port"]])
    print("Connecting to drive control...")
    drive_control = await connect(f"ws://{DRIVE_CONTROL_IP}:{DRIVE_CONTROL_PORT}")
    print("Starting server...")
    async with serve(handle_message, SERVE_IP, SERVE_PORT) as server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())