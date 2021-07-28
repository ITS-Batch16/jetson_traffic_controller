import cv2
import numpy as np
import copy
import threading
import time
from tracker.iou_tracker import IOU_Tracker as Tracker
from utils.utils import draw_boxes


__author__ = "Abarajithan G"
__copyright__ = "Copyright 2019, Final Year Project"
__credits__ = ["Abarajithan G", "Chinthana Wimalasuriya"]
__version__ = "1.0.0"
__maintainer__ = "Abarajthan G"
__email__ = "abarajithan07@gmail.com"
__status__ = "Research"


'''
Counts vehicles, weights flows, finds phase flows, takes moving average. This runs in a sub-thread.
'''
class WeightedFlowSensor(threading.Thread):
    def __init__(self,
                decode_netout,
                config,
                buffer=None,
                mode = "FLOW"  # FLOW / QUEUE
                ):
        super(WeightedFlowSensor, self).__init__()
        self.buffer = buffer
        self.tracker = None
        self.stop_flag = None
        self.config = config
        self.decode_netout = decode_netout
        self.mode = mode
        self.daemon = True
    
    def open(self):
        self.stop_flag = 0
        self.buffer = []
        self.start()

    def reset(self,mode):
        time.sleep(0.2)
        self.mode = mode
        self.tracker = None
        self.stop_flag = 0
        self.buffer = []
        for way_n in self.config.LANES.values():
            for lane in way_n.values():
                lane.lane_reset()
        
    
    def run(self):
        while ( self.stop_flag==0):
            if len(self.buffer) > self.config.MAX_NETOUT_BUFFER_SIZE:
                print('Buffer Overflow')
                break

            if len(self.buffer)==0:
                '''Skipping empty buffer'''
                continue
            
            cam_names, images, netout = self.buffer.pop(0)
            if netout is None:
                continue
            
            batch_size = len( netout)

            if self.tracker == None:
                self.tracker = dict(zip(cam_names,[Tracker() for i in range(batch_size)]))

            boxes = [self.decode_netout(netout[i].reshape(8,12,5,9), config=self.config) for i in range(batch_size)]
            images = [draw_boxes(images[i], boxes[i], labels=self.config.LABELS) for i in range(batch_size)]
            
            if self.mode == "FLOW":
                images = [self.after_frame(frame=images[i], boxes=boxes[i], way_n=cam_names[i]) for i in range(batch_size)]
                
                if self.config.SHOW_TRACKING:
                    '''Displaying the simultaneous tracking of 4 streams'''

                    if batch_size ==1:
                        images = images[0]
                    elif batch_size ==2:
                        images = np.hstack((images[0], images[1]))
                        images = cv2.resize(images, (768, 256))

                    elif batch_size == 4:
                        images = np.vstack(
                            (
                            np.hstack((images[0], images[1])),
                            np.hstack((images[2], images[3]))
                            )
                        )
                        images = cv2.resize(images, (768, 512))
                    cv2.imshow('TRACKING', images)
                    cv2.waitKey(1)
            
            elif self.mode == "QUEUE":
                pass

    def after_frame(self, frame,boxes, way_n):
        config=self.config

        self.tracker[way_n].associate(bboxes=boxes,
                               way_n=way_n,
                               config=config)
        if config.SHOW_TRACKING:
            frame = self.tracker[way_n].draw_tracking(frame, way_n, boxes,
                                               LABELS=config.LABELS,
                                               config=config)
        
        self.update_flow_measures(way_n=way_n, config=config)

        return frame


    def update_flow_measures(self, way_n, config):
        for track in self.tracker[way_n].tracks_leaving:
            '''
            Hold ghost tracks to prevent double counting
            '''
            track.left_count += 1

            if track.left_count > config.GHOST_BOX_DURATIONS[track.label_i]:
                #print("Label:    ", config.LABELS[track.label_i])
                self.tracker[way_n].tracks_leaving.remove(track)
                continue
            elif track.left_count > 1:
                continue

            x_center = (track.bbox_last.xmax + track.bbox_last.xmin)/2
            
            for lane in config.LANES[way_n].values():

                if lane.is_leaving_via(xmax=track.bbox_last.xmax, x_center=x_center, config=config):
                    #print(config.LABELS[track.label_i])
                    lane.flow_measure += config.PCU[track.label_i]
                    lane.count_measure[config.LABELS[track.label_i]] += 1

    #def update_queue_measure:

    def close(self):
        self.stop_flag = 1