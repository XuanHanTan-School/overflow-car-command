"""
Created on Mon Jan  20 02:07:13 2019

@author: prabhakar
"""
# import necessary argumnets 
import gi
import cv2
import argparse
from dotenv import dotenv_values

# import required library like Gstreamer and GstreamerRtspServer
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GLib

config = dotenv_values("config.env")
USERNAME = config["USERNAME"]
PASSWORD = config["PASSWORD"]

# Sensor Factory class which inherits the GstRtspServer base class and add
# properties to it.
class SensorFactory(GstRtspServer.RTSPMediaFactory):
    def __init__(self, opt, **properties):
        super(SensorFactory, self).__init__(**properties)
        self.opt = opt
        self.cap = cv2.VideoCapture(opt.device_id)
        self.number_frames = 0
        self.fps = opt.fps
        self.duration = 1 / self.fps * Gst.SECOND  # duration of a frame in nanoseconds
        self.launch_string = 'appsrc name=source is-live=true block=true format=GST_FORMAT_TIME ' \
                             'caps=video/x-raw,format=RGB,width={},height={},framerate={}/1 ' \
                             '! videoconvert ! video/x-raw,format=I420 ' \
                             '! x264enc speed-preset=ultrafast tune=zerolatency ' \
                             '! rtph264pay config-interval=1 name=pay0 pt=96' \
                             .format(opt.image_width, opt.image_height, self.fps)
    # method to capture the video feed from the camera and push it to the
    # streaming buffer.
    def on_need_data(self, src, length):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # It is better to change the resolution of the camera 
                # instead of changing the image shape as it affects the image quality.
                frame = cv2.resize(frame, (self.opt.image_width, self.opt.image_height), \
                    interpolation = cv2.INTER_LINEAR)
                data = frame.tostring()
                buf = Gst.Buffer.new_allocate(None, len(data), None)
                buf.fill(0, data)
                buf.duration = self.duration
                timestamp = self.number_frames * self.duration
                buf.pts = buf.dts = int(timestamp)
                buf.offset = timestamp
                self.number_frames += 1
                retval = src.emit('push-buffer', buf)
                # print('pushed buffer, frame {}, duration {} ns, durations {} s'.format(self.number_frames,
                #                                                                        self.duration,
                #                                                                        self.duration / Gst.SECOND))
                if retval != Gst.FlowReturn.OK:
                    print(retval)
    # attach the launch string to the override method
    def do_create_element(self, url):
        return Gst.parse_launch(self.launch_string)
    
    # attaching the source element to the rtsp media
    def do_configure(self, rtsp_media):
        self.number_frames = 0
        appsrc = rtsp_media.get_element().get_child_by_name('source')
        appsrc.connect('need-data', self.on_need_data)

# Rtsp server implementation where we attach the factory sensor with the stream uri
class GstServer(GstRtspServer.RTSPServer):
    def __init__(self, opt, **properties):
        super(GstServer, self).__init__(**properties)
        self.factory = SensorFactory(opt)
        self.factory.set_shared(True)
        self.set_service(str(opt.port))
        self.get_mount_points().add_factory("/video_stream", self.factory)

        # Set up basic authentication
        auth = GstRtspServer.RTSPAuth()
        token = GstRtspServer.RTSPToken()
        token.set_string(GstRtspServer.RTSP_TOKEN_MEDIA_FACTORY_ROLE, "user")
        basic = GstRtspServer.RTSPAuth.make_basic(USERNAME, PASSWORD)
        auth.add_basic(basic, token)
        self.set_auth(auth)

        permissions = GstRtspServer.RTSPPermissions()
        permissions.add_permission_for_role("user", "media.factory.access", True)
        permissions.add_permission_for_role("user", "media.factory.construct", True)
        self.factory.set_permissions(permissions)

        self.attach(None)

# Class to control RTSP thread
class RtspManager:
    def __init__(self, opt):
        # initializing the threads and running the stream on loop.
        Gst.init(None)
        self.server = GstServer(opt)
        self.loop = GLib.MainLoop()

    def start(self):
        try:
            print("Starting RTSP streaming...")
            self.loop.run()
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        print("Stopping RTSP streaming...")
        self.loop.quit()
        self.server.factory.cap.release()  # Release the OpenCV video capture
        Gst.deinit()
        print("Streaming stopped.")


parser = argparse.ArgumentParser()
parser.add_argument("--device_id", required=True, help="device id for the \
                video device or video file location")
parser.add_argument("--fps", required=True, help="fps of the camera", type = int)
parser.add_argument("--image_width", required=True, help="video frame width", type = int)
parser.add_argument("--image_height", required=True, help="video frame height", type = int)
parser.add_argument("--port", default=8554, help="port to stream video", type = int)
opt = parser.parse_args()

try:
    opt.device_id = int(opt.device_id)
except ValueError:
    pass

rtsp_manager = RtspManager(opt)
rtsp_manager.start()