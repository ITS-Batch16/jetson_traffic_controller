from video_streamer.streaming import RPIstreamer as streamer
from sensor.sensor import WeightedFlowSensor as Sensor
from cnn.tensorrt_uff import CNN
from utils.utils import decode_netout, memory_available
from config import config
import time
import gc

camera_names = ['COL', 'MAH', 'KES', 'PIL']
num_cameras = len(camera_names)

#starting camera thread
video_streamer = streamer(camera_names)

#Initializing sensor
sensor = Sensor(
    decode_netout=decode_netout,
    config=config,
    mode = "FLOW"
)

video_streamer.open()
sensor.open()
cnn = CNN(batch_size=num_cameras)
t_start=time.time()
tracking_time = 20
while True:
    
    #Inference with continous camera streams
    # images = [cameras[name].get_frame() for name in camera_names]
    images = video_streamer.get_frames()
    sensor.buffer.append(
        (images, cnn.batch_predict(images))
        )
    if time.time()-t_start>5:
        print(memory_available())
        gc.collect()
        print(memory_available())
        t_start = time.time()

    if time.time()-t_start >  tracking_time:
        break

sensor.close()
video_streamer.close()