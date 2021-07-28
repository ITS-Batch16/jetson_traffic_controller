from video_streamer.streaming import RPIstreamer as streamer
from sensor.sensor import WeightedFlowSensor as Sensor
from tracker.iou_tracker import IOU_Tracker as Tracker
from cnn.tensorrt_uff import CNN
from utils.utils import decode_netout, memory_available
from config import config
import time
import gc

old_f = sys.stdout
class F:
    def write(self, x):
        old_f.write(x.replace("\n", " [%s]\n" % str(datetime.now())))
sys.stdout = F()


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
REF_TIME =  time.time()-300
# QUEUE_CALC_INTERVAL = 2
# QUEUE_FRAMES = 10


while True:
    Traffic_flow = \
        {
            'COL': {
                'R': None,
                'S': None
            },
            'MAH': {
                'R':None,
                'S': None

            },
            'KES': {
                'R':None,
                'S': None
            },
            'PIL': {
                'R':None,
                'S': None
            },
        }
    t_now= time.time()
    t0 = t_now +CYCLE_TIME - (int(t_now -REF_TIME)%CYCLE_TIME)
    
    for Phase in config.PHASES:

        lanes = Phase.self.LANES
        cam_names = [lane.way_n for lane in lanes]
        
        phase_start = t0 + Phase.GREEN_STATIC[0]
        phase_end = phase_start + Phase.GREEN_STATIC[1]

        while(time.time() < phase_start)
        sensor.reset("FLOW")
        while(phase_start < time.time() < phase_end):
            images = video_streamer.get_frames(ret_dict = True)
            images = [images[cam_names[0]],images[cam_names[1]]]
            sensor.buffer.append(cam_names, images, cnn.batch_predict(images))
        for lane in lanes:
            Traffic_flow[lane.way_n][lane.name] = lane.flow_measure
        
        sensor.change_mode("QUEUE")
        # frame_count = 0
        # while( frame_count < QUEUE_FRAMES):
        #     images = video_streamer.get_frames(ret_dict = True)
        #     images = [images[cam_names[0]],images[cam_names[1]]]
        #     sensor.buffer.append(cam_names, images, cnn.batch_predict(images))
        #     frame_count+=1
        
        # for lane in lanes:
        #     Traffic_queue[lane.way_n][lane.name] = lane.queue_measure

    print(Traffic_flow)
    
    # calc_times()
    # send_to_dashborad()
    # reset_lane_measures()

