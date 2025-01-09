# Overflow Car (Command)

> WebSocket-Controlled RTSP Video Streaming and Motor Control

This project provides a framework to control a robotic vehicle with video streaming capabilities using WebSocket communication. It works great with the Overflow Car App, where you can use tilt gestures and a joystick to drive the car, along with a live video. It includes features such as RTSP video streaming, motor control, and authentication for secure access.

## Demo
<iframe width="560" height="315" src="https://www.youtube.com/embed/xpdiwNy15Jw?si=SkBaPZoYBdhs7LJN" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

## Features

- RTSP Video Streaming: Streams video using GStreamer and OpenCV.
- Motor Control: Connects to an internal WebSocket that handles driving commands to control any kind of vehicle.
- WebSocket Communication: Facilitates real-time control and data exchange.
- Secure Access: Password-protected access to ensure authorized usage.

## Setup and Installation

### Prerequisites

1. **Python**: Ensure Python 3.x is installed.
2. **System Dependencies**: Install the required libraries and dependencies using the following command:

```bash
sudo apt install python3-dev python3-gi python3-gi-cairo gir1.2-gtk-4.0 libcairo2-dev libgirepository1.0-dev libgstreamer1.0-0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-tools gstreamer1.0-x gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-gtk3 gstreamer1.0-qt5 gstreamer1.0-pulseaudio libglib2.0-dev libgstrtspserver-1.0-dev gstreamer1.0-rtsp
```
3. **Python Dependencies**: Install the required Python libraries using the following command:

```bash
pip install -r requirements.txt
```

## Usage

1. Configure Environment Variables:

   - Create a `config.env` file in the root directory.
   - Use `config.sample.env` as a template.

2. Run the Project:

- Start your motor control script, or for testing purposes, start the hardware simulation script:

```bash
python3 simulate-hardware.py
```

- Start the main WebSocket and RTSP server (camera streaming):

```bash
python3 main.py
```

3. (Optional) Access Remotely:
   - Use tools like Tailscale for remote access.

## Development

#### Directory Structure

- `stream.py` : Handles video streaming.
- `main.py` : Manages WebSocket communication.

#### Testing

To run this on a Pi-powered car, you may consult the [fork by Daksh Thapar](https://github.com/DakshRocks21/overflow-car-command/tree/main).

## Notes

- If you are using the Raspberry Pi Camera, OpenCV (used in `stream.py`) will have issues with it. See the fork by Daksh Thapar in the [Testing](#testing) section to find out how to use this with a Pi.

Have Fun! 🚗💨
