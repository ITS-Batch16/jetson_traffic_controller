import os
import sys
import utils.error_mngmnt as err

class ipcam:

    IP_DICT = { "COL" : "192.168.1.64",\
            "MAH" : "192.168.1.64",\
            "KES" : "192.168.1.64",\
            "PIL" : "192.168.1.64" }

    CAMERA_USERNAME = "admin"
    CAMERA_PASSWORD = "#fyp1234"
    STREAMING_PORT = 554
    STREAM_LOCATION= "/Streaming/Channels/102/"
    CAM_NAMES = IP_DICT.keys()
    URI_DICT = None

    @classmethod
    def unreachable_cams(cls,cam_names):
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
            ip = cls.IP_DICT[name]
            response = os.popen(f"ping {flag} {num_pckts} {ip}").read()
            search_results=[(keyword in response.lower()) for keyword in keywords]
            if any(search_results):
                unreachable_cam_list.append(name)

        if len(unreachable_cam_list) > 0:
            return unreachable_cam_list
        else:
            return None

    @classmethod
    def cam_init(cls):

        uri_list = []
        for name in cls.CAM_NAMES:
            uri="rtsp://%s:%s@%s:%s%s"%(cls.CAMERA_USERNAME, \
                cls.CAMERA_PASSWORD, cls.IP_DICT[name], \
                    cls.STREAMING_PORT, cls.STREAM_LOCATION)
            uri_list.append(uri)

        cls.URI_DICT = dict(zip(cls.CAM_NAMES,uri_list))

        # print("Inspecting cameras")
        # unreachable_cams = cls.unreachable_cams(cls.CAM_NAMES)

        # if unreachable_cams != None:
        #     err.CameraNotFoundError(unreachable_cams)

        print("All cameras are connected")




class rpi:

    IP_DICT = { "COL" : "192.168.1.101" ,\
                "MAH" : "192.168.1.101",\
                "KES" : "192.168.1.101",\
                "PIL" : "192.168.1.101" }

    STREAMING_PORT = { "COL" : "1111" ,\
                "MAH" : "2222",\
                "KES" : "1111",\
                "PIL" : "2222" }

    STREAM_LOCATION= "/video_feed"
    CAM_NAMES = IP_DICT.keys()
    URI_DICT = None

    @classmethod
    def unreachable_cams(cls,cam_names):
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
            ip = cls.IP_DICT[name]
            response = os.popen(f"ping {flag} {num_pckts} {ip}").read()
            search_results=[(keyword in response.lower()) for keyword in keywords]
            if any(search_results):
                unreachable_cam_list.append(name)

        if len(unreachable_cam_list) > 0:
            return unreachable_cam_list
        else:
            return None
    
    @classmethod
    def cam_init(cls):

        uri_list = []
        for name in cls.CAM_NAMES:
            uri="http://%s:%s%s"%( cls.IP_DICT[name], cls.STREAMING_PORT[name], cls.STREAM_LOCATION)
            uri_list.append(uri)

        cls.URI_DICT = dict(zip(cls.CAM_NAMES,uri_list))

        # print("Inspecting cameras")
        # unreachable_cams = cls.unreachable_cams(cls.CAM_NAMES)

        # if unreachable_cams != None:
        #     err.CameraNotFoundError(unreachable_cams)
            
        print("All cameras are connected")

