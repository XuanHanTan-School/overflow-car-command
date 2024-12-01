import json
from dotenv import dotenv_values
from websockets.sync.client import connect
from websockets.server import serve
import agorartc

config = dotenv_values("config.env")
DRIVE_CONTROL_IP = config["DRIVE_CONTROL_IP"]
DRIVE_CONTROL_PORT = int(config["DRIVE_CONTROL_PORT"])
SERVE_IP = config["SERVE_IP"]
SERVE_PORT = int(config["SERVE_PORT"])
CAR_ID = config["CAR_ID"]
AGORA_APP_ID = config["AGORA_APP_ID"]

drive_control = connect(f"ws://{DRIVE_CONTROL_IP}:{DRIVE_CONTROL_PORT}")
rtc = agorartc.createRtcEngineBridge()
event_handler = agorartc.RtcEngineEventHandlerBase()
rtc.initEventHandler(event_handler)
rtc.initialize(AGORA_APP_ID, None, agorartc.AREA_CODE_AS & 0xFFFFFFFF)

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
            start_video()
        elif message_type == "stop_video":
            stop_video()
        else:
            await websocket.send(json.dumps({"type": "error", "message": "Invalid message type"}))

def start_video():
    rtc.joinChannel("", CAR_ID, "", 0)
    rtc.enableVideo()
    rtc.disableAudio()

def stop_video():
    rtc.disableVideo()
    rtc.disableAudio()
    rtc.leaveChannel()
            
async def main():
    async with serve(handle_message, SERVE_IP, SERVE_PORT) as server:
        await server.serve_forever()