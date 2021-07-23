"""
Creates a configuration object which is then imported and passed to all functions.
Config object can be modified by the user (manually or via GUI)
"""
import time
import sys

def CameraError(cam_names):
    names = ", ".join(tuple(cam_names))
    msg = "Error! Unable to fetch frames from Camera %s"% names
    print(msg)
    sys.exit()


def CameraNotFoundError(cam_names) :
    names = ", ".join(tuple(cam_names))
    msg = "Error!  Camera %s not found" % names
    print(msg)
    sys.exit()