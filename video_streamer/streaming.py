import numpy as np
import rtsp
import utils.error_mngmnt as err
import video_streamer.cam_config as cfg
import time
import cv2 as cv
import threading
import requests

class RTSPstreamer:
    """
    Reads a live frame from  a given IP camera and returns a frame whenever requested.
    """

    def __init__(self,Camera_Names):
        """Constructor"""
        self.clients = None
        self.frame_timeout = 1 #seconds
        self.cam_names = Camera_Names
        if cfg.ipcam.URI_DICT == None:
            cfg.ipcam.cam_init()
        self.uri_dict = cfg.ipcam.URI_DICT

    def open(self):
        self.clients = [rtsp.Client(self.uri_dict[name]) for name in self.cam_names]
        print('video streams opened for cameras %s'%self.cam_names.__str__()[1:-1])
        
    def get_frames(self,ret_dict = False):
        """Returning the current frames when requested"""
        while(True):
            if self.clients is not None:
                break
            time.sleep(0.01)
        availability=[client.isOpened() for client in self.clients]
        
        if not all(availability):
            cam_list = np.array(self.cam_names)[np.array(availability) == False].tolist()
            err.CameraNotFoundError(cam_list)

        t0=time.time()
        while True:
            frames = [client.read(raw=True) for client in self.clients]
            null_frames = [(frame is None) for frame in frames]

            if not any(null_frames):
                t0=time.time()
                if ret_dict: return dict(zip(self.cam_names,frames))
                else: return frames
      
            if time.time()-t0 > self.frame_timeout:
                ret = np.array(self.cam_names)[null_frames].tolist()
                err.CameraError(ret)

    def close(self):
        for client in self.clients:client.close()
        time.sleep(1)
        print('video streams closed for cameras %s'%self.cam_names.__str__()[1:-1])


class RPIstreamer:
    """
    Reads a live frame from  a given Rpi-camera and returns a frame whenever requested.
    """

    def __init__(self, Camera_Names):
        """Constructor"""
        self.frames = None
        self.http_responses = None
        self.stop_flag = None
        self.cam_names = Camera_Names

        if cfg.rpi.URI_DICT == None:
            cfg.rpi.cam_init()

        self.uri_dict = cfg.rpi.URI_DICT
   
    def open(self):
        self.stop_flag = 0

        self.frames = [None] * len(self.cam_names)
        self.http_responses = [requests.get(self.uri_dict[name], stream=True) for name in self.cam_names]

        self.thread = threading.Thread(target=self.thread_function,daemon=True)
        self.thread.start()
        print('video streams opened for cameras %s'%self.cam_names.__str__()[1:-1])

    def thread_function(self):
        for lines in zip(*[rsp.iter_lines(chunk_size=512, delimiter=b'--frame', decode_unicode=False) for rsp in
                           self.http_responses]):
            frames = []

            if self.stop_flag == 1:
                for rsp in self.http_responses: rsp.close()
                break

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

    def get_frames(self,ret_dict = False):
        """Returning the current frames when requested"""
        if ret_dict: return dict(zip(self.cam_names,self.frames))
        else: return self.frames

    def close(self):
        self.stop_flag = 1
        time.sleep(1)
        print('video streams closed for cameras %s'%self.cam_names.__str__()[1:-1])

