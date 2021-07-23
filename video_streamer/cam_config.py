import os
import sys

class ipcam:

    IP_DICT = { "NORTH" : "192.168.1.101",\
            "EAST" : "192.168.1.102",\
            "SOUTH" : "192.168.1.103",\
            "WEST" : "192.168.1.104" }

    CAMERA_USERNAME = "admin"
    CAMERA_PASSWORD = "#fyp1234"
    STREAMING_PORT = 554
    STREAM_LOCATION= "/Streaming/Channels/102/"
    CAM_NAMES = IP_DICT.keys()

    @staticmethod
    def name_to_uri(cam_names):
        uri_list=[]
        for name in cam_names:
            uri="rtsp://%s:%s@%s:%s%s"%(ipcam.CAMERA_USERNAME, \
                ipcam.CAMERA_PASSWORD, ipcam.IP_DICT[name], \
                    ipcam.STREAMING_PORT, ipcam.STREAM_LOCATION)
            uri_list.append(uri)
        return uri_list

    URI_DICT = dict(zip(CAM_NAMES,name_to_uri(CAM_NAMES)))
    
    @staticmethod
    def unreachable_cams(cam_names):
        is_windows = sys.platform.startswith("win")

        flag = None
        keywords = ["unreachable","timed out"]
        num_pckts = 2

        if is_windows:
            flag = "-n"
        else:
            flag = "-c"

        unreachable_cam_list = []
        for name in cam_names:
            ip = ipcam.CAMERA_IP_DICT[name]
            response = os.popen(f"ping {flag} {num_pckts} {ip}").read()
            search_results=[(keyword in response.lower()) for keyword in keywords]
            if any(search_results):
                unreachable_cam_list.append(name)

        if len(unreachable_cam_list) > 0:
            return unreachable_cam_list
        else:
            return None



class rpi:

    IP_DICT = { "NORTH" : "192.168.1.101" ,\
                "EAST" : "192.168.1.102",\
                "SOUTH" : "192.168.1.103",\
                "WEST" : "192.168.1.104" }

    STREAMING_PORT = 80
    STREAM_LOCATION= "/video_feed"
    CAM_NAMES = IP_DICT.keys()

    def name_to_uri(cam_names):
        uri_list=[]
        for name in cam_names:
            uri="http://%s:%s%s"%( rpi.IP_DICT[name], rpi.STREAMING_PORT, rpi.STREAM_LOCATION)
            uri_list.append(uri)
        return uri_list

    URI_DICT = dict(zip(CAM_NAMES,name_to_uri(CAM_NAMES)))
    
    def unreachable_cams(cam_names):
        is_windows = sys.platform.startswith("win")

        flag = None
        keywords = ["unreachable","timed out"]
        num_pckts = 2

        if is_windows:
            flag = "-n"
        else:
            flag = "-c"

        unreachable_cam_list = []
        for name in cam_names:
            ip = rpi.RPI_IP_DICT[name]
            response = os.popen(f"ping {flag} {num_pckts} {ip}").read()
            search_results=[(keyword in response.lower()) for keyword in keywords]
            if any(search_results):
                unreachable_cam_list.append(name)

        if len(unreachable_cam_list) > 0:
            return unreachable_cam_list
        else:
            return None

