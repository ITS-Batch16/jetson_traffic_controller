from video_streamer.streaming import RPIstreamer as streamer
from sensor.sensor import WeightedFlowSensor as Sensor
from tracker.iou_tracker import IOU_Tracker as Tracker
from cnn.tensorrt_uff import CNN
from utils.utils import decode_netout, memory_available
from config import config
import time
import gc
import sys
from datetime import datetime
import copy

# old_f = sys.stdout
# class F:
#     def write(self, x):
#         old_f.write(x.replace("\n", " [%s]\n" % str(datetime.now())))
# sys.stdout = F()


camera_names = ['COL', 'MAH', 'KES', 'PIL']
num_cameras = len(camera_names)

#starting camera thread
video_streamer = streamer(camera_names)
video_streamer.open()

#Initializing sensor
sensor = Sensor(
    decode_netout=decode_netout,
    config=config
)

sensor.open()

cnn = CNN(batch_size= 2)
t_start=time.time()

CYCLE_TIME = config.CYCLE_TIME
REF_TIME =  time.time()-75
QUEUE_CALC_INTERVAL = 2
QUEUE_FRAMES = 10


while True:
    flow = copy.deepcopy(config.TRAFFIC_MEASURE_TEMPLATE)
    queue = copy.deepcopy(config.TRAFFIC_MEASURE_TEMPLATE)
    vehicle_count = copy.deepcopy(config.TRAFFIC_MEASURE_TEMPLATE)

    t_now= time.time()
    t0 = t_now +CYCLE_TIME - (int(t_now -REF_TIME)%CYCLE_TIME)
    count = 0
    for Phase in config.PHASES:
        count+=1
        lanes = Phase.LANES
        cam_names = [lane.way_n for lane in lanes]
        
        phase_start = t0 + Phase.GREEN_STATIC[0]
        phase_end = t0 + Phase.GREEN_STATIC[1]
        
        sensor.reset("FLOW")

        while(time.time() < phase_start):time.sleep(0.1)
        print(str(datetime.now())[:-7],"Green time started for phase %s and %s"%(cam_names[0],cam_names[1]))
        
        while(phase_start < time.time() < phase_end):
            images = video_streamer.get_frames(ret_dict = True)
            images = [images[cam_names[0]],images[cam_names[1]]]
            sensor.buffer.append((cam_names, images, cnn.batch_predict(images)))
        print(str(datetime.now())[:-7],"Green time ended for phase %d"%count)
        
        for lane in lanes:
            flow[lane.way_n][lane.name] = lane.get_flow_measure()
            vehicle_count[lane.way_n][lane.name] = lane.get_count_measure()
        
        sensor.reset("QUEUE")
   
        frame_count = 0
        while( frame_count < QUEUE_FRAMES):
            images = video_streamer.get_frames(ret_dict = True)
            images = [images[cam_names[0]],images[cam_names[1]]]
            sensor.buffer.append(cam_names, images, cnn.batch_predict(images))
            frame_count+=1
        
        for lane in lanes:
            queue[lane.way_n][lane.name] = lane.get_queue_measure()
             
        print("Switching Phase")

    print(flow)
    print(queue)
    print(flow)
    
    # calc_times()
    # send_to_dashborad()
    # reset_lane_measures()

