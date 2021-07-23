import time, cv2
import numpy as np
from video_streamer.streaming import RPIstreamer as streamer

'''Use each debug function to debug the system functionwise'''


def stream_cameras(CameraSet, active_cameras):
    '''Debuggginf function for receiving Ras/pi streams'''

    num_cameras = len(active_cameras)
    CameraSet.open(active_cameras )

    SHOW_TIME = 60
    t0 = time.time()
    images = [None] * num_cameras
    img_shape = None

    while (time.time() - t0 < SHOW_TIME):
        frames = CameraSet.get_frames()

        for i in range(num_cameras):
            frame = frames[i]
            if  frame is None:
                break
            if img_shape is None:
                img_shape = frame.shape
            cv2.putText(frame, active_cameras[i], (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255, 0), 3)
            images[i] = frame

    
        else:
            images2show = images+[np.zeros(img_shape, "uint8")]*(4-num_cameras)
            img_top = np.hstack((images2show[0], images2show[1]))
            img_bot = np.hstack((images2show[2], images2show[3]))
            img = np.vstack((img_top, img_bot))
            cv2.imshow('VIDEOS FROM CAMERAS', img)
            cv2.waitKey(1)
    
    cv2.destroyAllWindows()
    CameraSet.close()


if __name__ == '__main__':
    '''Run the required debugging function below.'''
    CameraSet = streamer()
    stream_cameras(CameraSet,["NORTH","SOUTH"])
    stream_cameras(CameraSet,["EAST","SOUTH","WEST"])
    stream_cameras(CameraSet,["SOUTH"])
    stream_cameras(CameraSet,["EAST","SOUTH","WEST","NORTH"])