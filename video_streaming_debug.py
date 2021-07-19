import time, cv2
import numpy as np
from video_streamer.streaming import RTSPstreamer as streamer
import video_streamer.cam_config as cfg


'''Use each debug function to debug the system functionwise'''


def stream_cameras():
    '''Debuggginf function for receiving Ras/pi streams'''
    camera_names = cfg.CAMERA_NAMES
    num_cameras = cfg.NUM_CAMERAS
    CameraSet = streamer()

    SHOW_TIME = 600
    t0 = time.time()
    images = [None] * num_cameras

    while (time.time() - t0 < SHOW_TIME):
        frames = CameraSet.get_frames()

    #     for i in range(num_cameras):
    #         if frames[i] is None:
    #             break
    #         cv2.putText(frames[i], camera_names[i], (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255, 0), 3)
    #         images[i] = frames[i]
    #
    #     else:
    #         image_dict = dict(zip(camera_names, images))
    #         img_top = np.hstack((image_dict['NORTH'], image_dict['EAST']))
    #         img_bot = np.hstack((image_dict['SOUTH'], image_dict['WEST']))
    #         img = np.vstack((img_top, img_bot))
    #         cv2.imshow('VIDEOS FROM CAMERAS', img)
    #         cv2.waitKey(1)
    #
    # cv2.destroyAllWindows()
    CameraSet.close()


if __name__ == '__main__':
    '''Run the required debugging function below.'''
    stream_cameras()