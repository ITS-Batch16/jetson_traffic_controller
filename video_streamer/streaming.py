import numpy as np
import rtsp
import utils.error_mngmnt as err
import cam_config as cam_cfg
import rpi_config as rpi_cfg
import time
import cv2 as cv
import sys

class RTSPstreamer:
    """
    Reads a live frame from  a given IP camera and returns a frame whenever requested.
    """

    def __init__(self):
        """Constructor"""
        self.clients = None
        self.frame_timeout = 1

        cams = cam_cfg.unreachable_cams()

        if cams == None:

            self.clients = [rtsp.Client(URI) for URI in cam_cfg.CAMERA_URI_LIST]
        else:
            err.CameraNotFoundError(cams)

    def get_frames(self):
        """Returning the current frames when requested"""
        while(True):
            if self.clients is not None:
                break
            time.sleep(0.01)
        availability=[client.isOpened() for client in self.clients]
        
        if not all(availability):
            cam_list = np.array(cam_cfg.CAMERA_NAMES)[np.array(availability) == False].tolist()
            err.CameraNotFoundError(cam_list)

        t0=time.time()
        while True:
            frames = [client.read(raw=True) for client in self.clients]
            null_frames = [(frame is None) for frame in frames]

            if not any(null_frames):
                t0=time.time()
                return frames
      
            if time.time()-t0 > self.frame_timeout:
                ret = np.array(cam_cfg.CAMERA_NAMES)[null_frames].tolist()
                #print(ret)
                err.CameraError(ret)

    def close(self):
        for client in self.clients:client.close()
        print('Camera thread closed')


class streamerRpi(threading.Thread):
    """
    Reads a live frame from  a given Rpi-camera and returns a frame whenever requested.
    """

    def __init__(self):
        """Constructor"""
        super(streamerRpi, self).__init__()
        self.URI_list = video_uris.values()
        self.frames = None
        self.http_responses = None
        self.stop_flag = None
        self.num_cameras = len(self.URI_list)

        print('Camera thread opened')

    def begin(self):
        """Starting the thread """
        self.stop_flag = 0
        self.frames = [None] * self.num_cameras
        self.http_responses = [requests.get(URI, stream=True) for URI in self.URI_list]
        self.start()

    def run(self):
        for lines in zip(*[rsp.iter_lines(chunk_size=512, delimiter=b'--frame', decode_unicode=False) for rsp in
                           self.http_responses]):

            if self.stop_flag == 1:
                for rsp in self.http_responses: rsp.close()
                break

            frames = []

            for line in lines:
                response = line.split(b'\r\n\r\n')

                if len(response) != 2:
                    break
                response_header = str(response[0][2:])
                response_body = response[1][:-2]
                frame_data = np.asarray(bytearray(response_body), dtype="uint8")
                frames.append(cv.imdecode(frame_data, cv.IMREAD_COLOR))

            else:
                self.frames = frames

    def get_frames(self):
        """Returning the current frames when requested"""
        return self.frames

    def close(self):
        self.stop_flag = 1
        print('Camera thread closed')

