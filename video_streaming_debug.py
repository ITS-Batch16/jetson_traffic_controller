import time, cv2
import numpy as np
from video_streamer.streaming import RTSPstreamer as streamer

'''Use each debug function to debug the system functionwise'''


def stream_cameras(active_cameras):
    '''Debuggginf function for receiving Ras/pi streams'''

    video_streamer = streamer(active_cameras)
    num_cameras = len(active_cameras)
    video_streamer.open()
    SHOW_TIME = 10
    t0 = time.time()
    images = [None] * num_cameras
    img_shape = None

    while (time.time() - t0 < SHOW_TIME):
        frames = video_streamer.get_frames()

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
    video_streamer.close()
    del video_streamer
    time.sleep(5)


if __name__ == '__main__':
    '''Run the required debugging function below.'''
    # stream_cameras(["NORTH","SOUTH"])
    #stream_cameras(["EAST","SOUTH","WEST"])
    # stream_cameras(["SOUTH"])
    stream_cameras(["EAST","SOUTH","WEST","NORTH"])
