

import os
import sys

RPI_IP_DICT = { "NORTH" : "192.168.1.101" ,
           "EAST" : "192.168.1.102" }
           # "SOUTH" : "192.168.1.103" ,
           #  "WEST" : "192.168.1.104" }

STREAMING_PORT = 80
STREAM_LOCATION= "/video_feed"
CAMERA_IP_LIST = list(RPI_IP_DICT.values())
CAMERA_NAMES = list(RPI_IP_DICT.keys())
NUM_CAMERAS=len(CAMERA_NAMES)

def ip_to_uri(ip_list):
    uri_list=[]
    for ip in ip_list:
        uri="http://%s:%s%s"%( ip, STREAMING_PORT, STREAM_LOCATION)
        uri_list.append(uri)
    return uri_list


CAMERA_URI_LIST = ip_to_uri(CAMERA_IP_LIST)


def unreachable_cams():
    is_windows = sys.platform.startswith("win")

    flag = None
    keywords = ["unreachable","timed out"]
    num_pckts = 2

    if is_windows:
        flag = "-n"
    else:
        flag = "-c"

    unreachable_cam_list = []
    for i in range(len(CAMERA_IP_LIST)):
        ip = CAMERA_IP_LIST[i]
        response = os.popen(f"ping {flag} {num_pckts} {ip}").read()
        search_results=[(keyword in response.lower()) for keyword in keywords]
        if any(search_results):
            unreachable_cam_list.append(CAMERA_NAMES[i])

    if len(unreachable_cam_list) > 0:
        return unreachable_cam_list
    else:
        return None