
'''
Creates a configuration object which is then imported and passed to all functions.
Config object can be modified by the user (manually or via GUI)
'''

__author__ = "Abarajithan G"
__copyright__ = "Copyright 2019, Final Year Project"
__credits__ = ["Abarajithan G"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Abarajthan G"
__email__ = "abarajithan07@gmail.com"
__status__ = "Research"
from sympy import Point,Line
import math

class Config():
    def __init__(self):
        self.DEBUG = True
        self.PRINT_DEBUG_LOG = False
        self.SHOW_TRACKING = True
        self.SAVE_TRACKING_VIDEO = False
        self.SAVE_TRACKING_FRAMES = False

        self.FRAME_STREAM_PREFIX = 'data/frames_input/debug_'
        self.FRAME_STREAM_POSTFIX = '.jpg'
        self.FRAME_STREAM_i = 1
        self.FRAME_STREAM_SAVE_PREFIX = 'data/log/tracked_frames/'

        self.SHOW_TRACK = True
        self.SHOW_BBOX = False
        self.SHOW_BBOX_PREV = False
        self.SHOW_BBOX_PREDICTED = False
        self.SHOW_BBOX_LEAVING = True
        self.SHOW_BBOX_GHOST = False
        self.SHOW_REGIONS = False
        self.SHOW_LANES = False

        self.DIRECTORY_PATH = 'data/video_input/'
        self.LOG_PATH = 'data/log/'
        self.FILENAMES = ['e_c_2.MOV', 'e_c.MOV', 'e_l_2.MOV',
                          'e_l.MOV', 'n.MOV', 's.MOV', 'w_c.MOV', 'w_l.MOV']
        self.PROCESSING_FPS = 10
        self.H_SHOW = 480
        self.W_SHOW = 640

        self.COLOR_LANES = (0, 255, 0)
        self.COLOR_REGIONS = (0, 0, 255)
        self.COLOR_BBOX = (0, 255, 0)
        self.COLOR_BBOX_LAST = (255, 0, 255)
        self.COLOR_BBOX_PREDICTED = (0, 0, 255)
        self.COLOR_BBOX_COUNTED = (255, 0, 0)
        self.COLOR_TRACK = (0, 255, 255)
        self.COLOR_TRACK_BROKEN = (0, 0, 0)
        self.LINE_THICKNESS = 1

        self.Y_MIN_RATIO = 1/3
        self.Y_MAX_START_RATIO = 15/16
        self.X_MAX_START_RATIO = 14/16
        self.Y_MAX_END_RATIO = 31/32
        self.X_MAX_END_RATIO = 31/32
        self.IOU_TRACKING_THRESHOLD = 0.2
        self.START_TRACK_THRESHOLD = 0.3
        self.REMOVE_AFTER_FRAMES = 5
        self.MISSED_BBOX_ENLARGE_FACTOR = 1.5
        self.SPEED_FACTOR_X = 1
        self.SPEED_FACTOR_Y = 1.5
        self.GHOST_BOX_DURATIONS = [3, 3, 4, 15]

        self.PCU = [0.6, 0.9, 1.1, 2.3]
        self.AVG_CYCLES = 1
        self.GREEN_MAX = 27
        self.GREEN_MIN = 7
        self.GREEN_DELTA = 50  # 20
        self.MIN_TOTAL_MEASURE = 5  # vehicles per minute

        self.GAMMA = 2.2
        self.WEIGHTS_PATH = 'cnn/yolov2_weights_oct.h5'
        self.LABELS = ['motorbike', 'three-wheeler', 'car', 'truck']
        self.W_NN_INPUT = 384
        self.H_NN_INPUT = 256
        self.OBJ_THRESHOLD = 0.5
        self.NMS_THRESHOLD = 0.3
        self.ANCHORS = [0.57273, 0.677385, 1.87446, 2.06253,
                        3.33843, 5.47434, 7.88282, 3.52778, 9.77052, 9.16828]
        self.NUM_CLASSES = 4
        self.TRAFFIC_MEASURE_TEMPLATE =Traffic_flow = \
        {
            'COL': {
                'R': None,
                'S': None,
                'L':None
            },
            'MAH': {
                'R':None,
                'S': None,
                'L':None

            },
            'KES': {
                'R':None,
                'S': None,
                'L':None
            },
            'PIL': {
                'R':None,
                'S': None,
                'L':None
                
            },
        }

        self.LANES = {
            'COL': {
                'R': Lane(name='R',
                          way_n = 'COL',
                          phase=3,
                          x_limits=(0.1039,0.2945),
                          left_boubdary=((0.1039,0.968),(0.4055,0.2777)),
                          right_boubdary=((0.2945,0.968),(0.4570,0.2777))),

                'S': Lane(name='S',
                           way_n = 'COL',
                           phase=3,
                           x_limits=(0.2945, 0.5437),
                           left_boubdary=((0.2945,0.968),(0.4570,0.2777)),
                           right_boubdary=((0.5437,0.968),(0.5656,0.2777))),

                'L': Lane(name='L',
                          way_n = 'COL',
                          phase=-1,
                          x_limits=(0.5437,0.9687),
                          left_boubdary=((0.5437,0.968),(0.5656,0.2777)),
                          right_boubdary=((1,0.7903),(0.6031,0.2777))),

            },
            'MAH': {
                'R': Lane(name='R',
                          way_n = 'MAH',
                          phase=2,
                          x_limits=(0.3023, 0.5656),
                          left_boubdary=((0.3023,0.968),(0.4570,0.2777)),
                          right_boubdary=((0.5656,0.968),(0.5195,0.2777))),

                'S': Lane(name='S',
                          way_n = 'MAH',
                          phase=1,
                          x_limits=(0.5656,0.8),
                          left_boubdary=((0.5656,0.968),(0.5195,0.2777)),
                          right_boubdary=((0.8,0.968),(0.5953,0.2777))),

                'L': Lane(name='L',
                          way_n = 'MAH',
                          phase=-1,
                          x_limits=(0.8,0.9687),
                          left_boubdary=((0.8,0.968),(0.5953,0.2777)),
                          right_boubdary=((1,0.7361),(0.6289,0.2777))),
            },
            'KES': {
                'R': Lane(name='R',
                          way_n = 'KES',
                          phase=4,
                          x_limits=(0.1070, 0.3125),
                          left_boubdary=((0.1070,0.968),(0.4437,0.2777)),
                          right_boubdary=((0.3125,0.968),(0.4867,0.2777))),

                'S': Lane(name='S',
                           way_n = 'KES',
                           phase=4,
                           x_limits=(0.3125, 0.7679),
                           left_boubdary=((0.3125,0.968),(0.4867,0.2777)),
                           right_boubdary=((0.7679,0.968),(0.5734,0.2777))),

                'L': Lane(name='L',
                          way_n = 'KES',
                          phase=0,
                          x_limits=(0.7679, 0.9687),
                          left_boubdary=((0.7679,0.968),(0.5734,0.2777)),
                          right_boubdary=((1,0.9028),(0.5859,0.2777))),
            },
            'PIL': {
                'R': Lane(name='R',
                          way_n = 'PIL',
                          phase=2,
                          x_limits=(0.2547, 0.4687),
                          left_boubdary=((0.2547,0.968),(0.4414,0.2777)),
                          right_boubdary=((0.4687,0.968),(0.4664,0.2777))),
                'S': Lane(name='S',
                          way_n = 'PIL',
                          phase=1,
                          x_limits=(0.4687, 0.7602),
                          left_boubdary=((0.4687,0.968),(0.4664,0.2777)),
                          right_boubdary=((0.7602,0.968),(0.5352,0.2777))),

                'L': Lane(name='L',
                          way_n = 'PIL',
                          phase=0,
                          x_limits=(0.7602, 0.9687),
                          right_boubdary=((0.7602,0.968),(0.5352,0.2777))),
                          right_boubdary=((1,0.875),(0.5727,0.2777))),
            }
        }

        self.CYCLE_TIME = 80
        self.PHASES = [
            Phase(
                LANES=[
                    self.LANES['PIL']['S'],
                    self.LANES['MAH']['S']
                ],
                GREEN_STATIC=(2,18)),

            Phase(
                LANES=[
                    self.LANES['PIL']['R'],
                    self.LANES['MAH']['R']
                ],
                GREEN_STATIC=(22,38)),

            Phase(
                LANES=[
                    self.LANES['COL']['S'],
                    self.LANES['COL']['R']
                ],
                GREEN_STATIC=(42,58)),

            Phase(
                LANES=[
                    self.LANES['KES']['S'],
                    self.LANES['KES']['R']
                ],
                GREEN_STATIC=(62,78))
        ]
        
        self.MAX_NETOUT_BUFFER_SIZE=700

       # TODO : Opposing flows - Through Equivalent Volume

        self.num_cycles = 0
        self.set_param()

    def set_param(self):
        self.NUM_PHASES = len(self.PHASES)
        #self.GREEN_TOTAL = sum([phase.GREEN_STATIC for phase in self.PHASES])

        # assert self.GREEN_MIN < (
        #     self.GREEN_TOTAL / self.NUM_PHASES) < self.GREEN_MAX

        self.Y_MIN = int(self.H_SHOW * self.Y_MIN_RATIO)
        self.Y_MAX_START = int(self.H_SHOW * self.Y_MAX_START_RATIO)
        self.X_MAX_START = int(self.W_SHOW * self.X_MAX_START_RATIO)
        self.Y_MAX_END = int(self.H_SHOW * self.Y_MAX_END_RATIO)
        self.X_MAX_END = int(self.W_SHOW * self.X_MAX_END_RATIO)


# class Line:
#     def __init__(self, p1, p2):
#         self.set_m_c(p1, p2)

#     def is_less(self, p):
#         x, y = p
#         return x <= self.m * y + self.c

#     def set_m_c(self, p1, p2):
#         self.points = p1, p2
#         x1, y1 = p1
#         x2, y2 = p2
#         self.m = (x1-x2)/(y1-y2)  # delta(y)/delta(x)
#         self.c = x1 - self.m*y1




class Lane:
    '''
    ATTRIBUTES
    - phase         : to which phase this lane belongs to
    - x_limits      : (xmin, xmax) range of this lane
    - measure       : flow or density or anything that we measure
    - flow_measure : updated every frame, reset at end of cycle

    NOTE
    * After each frame, flow_measure is updated by Tracker.update_flow_measure(bboxes)
    * After each cycle, all measures are updated and flow_measures reset by Tracker.update_measures()

    METHODS
    - add_to_temp:  Updates flow_measure of this lane IF bbox belongs here
    '''

    def __init__(self, name, way_n, phase, x_limits=None, left_boubdary = None,right_boubdary = None):
        self.name = name
        self.way_n = way_n
        self.phase = phase
        self.x_limits = min(x_limits), max(x_limits)
        self.left_boubdary = left_boubdary
        self.right_boubdary = right_boubdary
        self.flow_measure = 0
        self.queue_measure = 0
        self.queue_frame_count = 0
        self.count_measure = dict(zip(['motorbike', 'three-wheeler', 'car', 'truck'],[0,0,0,0]))

    def is_leaving_via(self, xmax, x_center, config):
        if self.name == 'L':
            if xmax > config.X_MAX_END_RATIO:
                # print('lane', 'lL')
                return True
        else:
            if self.x_limits[0] <= x_center <= self.x_limits[1]:
                return True
                # print('lane', lane.name)

    def is_on_lane(self,point):
        l1 = Line(self.left_boubdary)
        l2 = Line(self.right_boubdary)
        p = Point(point)
        pl1 = l1.perpendicular_line(p)
        pl2 = l2.perpendicular_line(p)

        angle = float(pl1.smallest_angle_between(pl2))

        if angle < math.pi*0.5:
            return True
        else:
            return False

    
    def get_flow_measure(self):
        return self.flow_measure

    def get_queue_measure(self):
        try:
            return self.queue_measure/self.queue_frame_count
        except:
            print("Error! queue length calculation not called")
            return 0

    def get_count_measure(self):
        return self.count_measure

    def lane_reset(self):
        self.flow_measure = 0
        self.queue_measure = 0
        self.count_measure = dict(zip(['motorbike', 'three-wheeler', 'car', 'truck'],[0,0,0,0]))


    

class Phase:
    def __init__(self, LANES, GREEN_STATIC):
        self.LANES = LANES
        self.GREEN_STATIC = GREEN_STATIC
        self.flow_measure = 0
        self.cycle_ratio = 0
        self.smooth_measure = 0
        self.green_dynamic = GREEN_STATIC

    def get_critical_measure(self):
        '''
        Critical flow is max flow among cycles
        '''
        # Get PCU weighted critical count
        self.flow_measure = max([group.get_flow_measure()
                                  for group in self.LANE_GROUPS])
        '''
        Get criical flow. Two possible ways:

        1. Divide counts by cycle time (or not divide at all). 
            * Corresponds to hourly volumes through the lanes.
        2. Divide counts by last green time.
            * Corresponds to actual dynamic flows through the lanes.

        Pros & Cons:
            * (1) is as in webster's method. Suitable for static timing
              because phase timing doesn't change throughout the day.
            * But when dynamically done in a scenario where two phases (A,B) 
              are equally congested, phase (A) that got highest time in
              last cycle would have allowed more vehicles. 
            * Then (1) would allocate more time to (A), which would
              result in (A) sending more vehicles and (B) forming a snake.
              In next cycle (A) gets even more time.
            * Hence (1) is divergent.

            * (2) would allocate equal ratios to (A) and (B) if flows are equal.
            * If a phase (C) gets more time and does not send propotionally more 
              vehicles, its time would get reduced. 
            * (2) gives error correction, but oscillations are possible.
        '''
        self.flow_measure /= self.green_dynamic

        return self.flow_measure

    def get_smooth_measure(self, config):
        config.num_cycles += 1
        '''
        Moving average across cycles
        '''
        self.smooth_measure += (self.flow_measure - self.smooth_measure) / \
            min(config.num_cycles, config.AVG_CYCLES)

config = Config()