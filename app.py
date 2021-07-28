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


Phase_conf = { "P1":{
                    "cams":["MAH","PIL"],
                    "lanes":["STRAIGHT","STRAIGHT"],
                    "phase_time":[2,10]
                    },

                "P2":{
                    "cams":["MAH","PIL"],
                    "lanes":["RIGHT","RIGHT"],
                    "phase_time":[13,10]
                    },

                "P3":{
                    "cams":["MAH","PIL"],
                    "lanes":["RIGHT","RIGHT"],
                    "phase_time":[13,10]
                    },
                "P4":{
                    "cams":["MAH","PIL"],
                    "lanes":["RIGHT","RIGHT"],
                    "phase_time":[13,10]
                    },
                    



CYCLE_TIME = 60
REF_TIME =  
QUEUE_CALC_INTERVAL = 2
QUEUE_FRAMES = 10


while True:
    # if plc.cycle_start == True :
    #     for Phase in Phases_conf:
    #         while(plc.status == "OFF-GREEN"):time.sleep(0.1)
    #         while(plc.status == "ON-GREEN"):

    
    que_lengths ={} , pcu_counts ={}  , vehicle_counts = {}

    for phase in Phase_conf:
        cam_names = phase["cams"]
        lanes = phase["lanes"]
        phase_start = t0 + 
        phase_end = 
 
        while(time.time() < phase_start)
        sensor.change_mode("FLOW")
        while(phase_start < time.time() < phase_end):
            images = video_streamer.get_frames(ret_dict = True)
            images = [images[cam_names[0]],images[cam_names[1]]]
            sensor.buffer.append(cam_names, images, cnn.batch_predict(images))
        
        sensor.change_mode("QUEUE")
        frame_count = 0
        while( frame_count < QUEUE_FRAMES):
            images = video_streamer.get_frames(ret_dict = True)
            images = [images[cam_names[0]],images[cam_names[1]]]
            sensor.buffer.append(cam_names, images, cnn.batch_predict(images))
            frame_count+=1

        que_lengths , pcu_counts , vehicle_counts  = sensor.out_params()
    
    calc_times()
    send_to_dashborad()
    reset_lane_measures()




    








    else:
        continue

