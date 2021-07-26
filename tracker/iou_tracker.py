'''
IOU based tracker that tracks vehicles,
'''

import copy
import cv2
import numpy as np

__author__ = "Abarajithan G"
__copyright__ = "Copyright 2019, Final Year Project"
__credits__ = ["Abarajithan G"]
__version__ = "1.0.0"
__maintainer__ = "Abarajthan G"
__email__ = "abarajithan07@gmail.com"
__status__ = "Research"


class Track:
    def __init__(self, bbox, config):
        '''
        Initial velocity is assumed as half the bbox height.
        Assuming vehicle always comes towards the camera
        '''
        self.delta_x = 0
        self.delta_y = (bbox.xmax - bbox.xmin)/2

        self.bbox_last = copy.deepcopy(bbox)
        self.bbox_predicted = copy.deepcopy(bbox)

        self.archive = []  # To draw the track only
        self.bbox_predicted_last = None  # To draw only

        self.bbox_predicted.xmax += self.delta_x
        self.bbox_predicted.xmin += self.delta_x
        self.bbox_predicted.ymax += self.delta_y
        self.bbox_predicted.ymin += self.delta_y

        self.miss_count = 0
        self.left_count = 0

        self.cum_confidences = bbox.c * bbox.classes  # Numpy array
        self.confidence = bbox.c * bbox.score
        self.label_i = bbox.label

    def update(self, bbox, config):

        self.archive += [self.bbox_last]  # To draw the track only
        self.bbox_predicted_last = self.bbox_predicted  # To draw only

        x_1 = (self.bbox_last.xmax + self.bbox_last.xmin)/2
        y_1 = (self.bbox_last.ymax + self.bbox_last.ymin)/2

        x_0 = (bbox.xmax + bbox.xmin)/2
        y_0 = (bbox.ymax + bbox.ymin)/2

        self.delta_x = x_0 - x_1
        self.delta_y = y_0 - y_1

        self.bbox_last = copy.deepcopy(bbox)
        self.bbox_predicted = copy.deepcopy(bbox)

        self.bbox_predicted.xmax += self.delta_x * config.SPEED_FACTOR_X
        self.bbox_predicted.xmin += self.delta_x * config.SPEED_FACTOR_X
        self.bbox_predicted.ymax += self.delta_y * config.SPEED_FACTOR_Y
        self.bbox_predicted.ymin += self.delta_y * config.SPEED_FACTOR_Y

        self.miss_count = 0

        '''
        The class confidences (scaled by object confidence) are accumulated
        along the track for better prediction.
        '''
        self.cum_confidences += bbox.c * bbox.classes  # Numpy array
        self.confidence = np.max(self.cum_confidences) / \
            np.sum(self.cum_confidences)
        self.label_i = np.argmax(self.cum_confidences)

    def update_missed(self, config):
        self.bbox_predicted.xmax += self.delta_x * config.SPEED_FACTOR_X
        self.bbox_predicted.xmin += self.delta_x * config.SPEED_FACTOR_X
        self.bbox_predicted.ymax += self.delta_y * config.SPEED_FACTOR_Y
        self.bbox_predicted.ymin += self.delta_y * config.SPEED_FACTOR_Y


class IOU_Tracker:
    def __init__(self):
        self.tracks = []
        self.tracks_leaving = []

    def associate(self, bboxes, way_n, config):
        '''
        Deepcopy to keep the original boxes intact for drawing
        '''
        bboxes = copy.deepcopy(bboxes)

        for track in self.tracks:
            bbox = None
            iou_max = config.IOU_TRACKING_THRESHOLD

            '''
            Remove tracks that leave through top
            '''
            if track.bbox_last.ymax < config.Y_MIN_RATIO:

                if config.PRINT_DEBUG_LOG:
                    print(
                        f"Removing {config.LABELS[track.label_i]}: outside ymax")

                self.tracks.remove(track)
                continue

            '''
            Find the best match bbox
            '''
            for bbox_check in bboxes:
                '''
                Delete boxes that has not entered
                '''
                if bbox_check.ymax < config.Y_MIN_RATIO:
                    bboxes.remove(bbox_check)
                    continue

                iou = IOU_Tracker.bbox_iou(track.bbox_last, bbox_check)

                if iou > iou_max:
                    iou_max = iou
                    bbox = bbox_check

            '''
            If best bbox is found, update track. 
            Else, handle the broken track
            '''
            if bbox is not None:
                track.update(bbox=bbox, config=config)
                '''
                If vehicle is leaving, move it to seperate list
                '''
                vehicle_leaving = bbox.ymax > config.Y_MAX_END_RATIO or bbox.xmax > config.X_MAX_END_RATIO
                bboxes.remove(bbox)

                '''
                Prevent Double counting
                '''
                is_double = False
                for left_track in self.tracks_leaving:
                    #print("IOU----------------------> ",
                    #      IOU_Tracker.bbox_iou(track.bbox_last, left_track.bbox_last))
                    if IOU_Tracker.bbox_iou(track.bbox_last, left_track.bbox_last) > 0.5:
                        is_double = True

                if is_double:
                    self.tracks.remove(track)
                    continue

                if vehicle_leaving:
                    self.tracks_leaving += [track]
                    self.tracks.remove(track)

                    if config.PRINT_DEBUG_LOG:
                        print(f"{config.LABELS[track.label_i]} is leaving")
            else:
                if track.miss_count > config.REMOVE_AFTER_FRAMES:
                    self.tracks.remove(track)
                else:
                    track.miss_count += 1
                    track.update_missed(config=config)

            '''
            Trim Track Archives to save memory
            '''
            if len(track.archive) > 10:
                track.archive.pop(0)

        '''
        Create tracks for unassigned bboxes that have entered
        '''
        for bbox in bboxes:
            if bbox.ymax > config.Y_MIN_RATIO and bbox.ymax < config.Y_MAX_START_RATIO and bbox.xmax < config.X_MAX_START_RATIO:
                if bbox.c > config.START_TRACK_THRESHOLD:

                    self.tracks += [Track(bbox=bbox, config=config)]

                    if config.PRINT_DEBUG_LOG:
                        print(
                            f"{config.LABELS[bbox.get_label()]} is entering, creating track")

            bboxes.remove(bbox)

    def reset(self):
        self.tracks = []

    def draw_tracking(self, frame, way_n,
                      bboxes,
                      config,
                      LABELS=None):
        frame = cv2.resize(frame, (config.W_SHOW, config.H_SHOW))

        if config.SHOW_REGIONS:
            cv2.rectangle(frame,
                          (0, config.Y_MIN),
                          (config.X_MAX_END, config.Y_MAX_END),
                          config.COLOR_REGIONS,
                          config.LINE_THICKNESS)
            cv2.rectangle(frame,
                          (0, config.Y_MIN),
                          (config.X_MAX_START, config.Y_MAX_START),
                          config.COLOR_REGIONS,
                          config.LINE_THICKNESS)
        if config.SHOW_LANES:
            for lane in config.LANES[way_n].values():
                cv2.line(frame,
                         (int(config.W_SHOW * lane.x_limits[0]), 0),
                         (int(config.W_SHOW *
                              lane.x_limits[0]), config.W_SHOW-1),
                         config.COLOR_LANES,
                         config.LINE_THICKNESS)
                cv2.line(frame,
                         (int(config.W_SHOW * lane.x_limits[1]), 0),
                         (int(config.W_SHOW *
                              lane.x_limits[1]), config.W_SHOW-1),
                         config.COLOR_LANES,
                         config.LINE_THICKNESS)

        def get_b_center(bbox, config):
            return int(config.W_SHOW * (bbox.xmax + bbox.xmin) / 2), int(config.H_SHOW * bbox.ymax)

        def draw_bbox(frame,
                      bbox,
                      color,
                      text='',
                      thickness=config.LINE_THICKNESS):

            xmin = int(bbox.xmin * config.W_SHOW)
            ymin = int(bbox.ymin * config.H_SHOW)
            xmax = int(bbox.xmax * config.W_SHOW)
            ymax = int(bbox.ymax * config.H_SHOW)

            cv2.rectangle(frame,
                          (xmin, ymin),
                          (xmax, ymax),
                          color,
                          thickness)

            cv2.putText(frame,
                        text,
                        (xmin, ymin - 13),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1e-3 * config.H_SHOW,
                        color,
                        thickness)

        for track in self.tracks_leaving:

            if len(track.archive):
                '''
                GHOST BOXES (White)
                '''
                text = f"{LABELS[track.label_i]} {track.confidence:.2f}"

                if config.SHOW_BBOX_GHOST:
                    if track.left_count > 0:
                        draw_bbox(frame,
                                  bbox=track.archive[-1],
                                  color=(255, 255, 255),
                                  thickness=config.LINE_THICKNESS*2,
                                  text=text)
                        continue
                '''
                LEAVING TRACKS
                '''
                if config.SHOW_BBOX_LEAVING:
                    draw_bbox(frame,
                              bbox=track.archive[-1],
                              color=config.COLOR_BBOX_COUNTED,
                              thickness=config.LINE_THICKNESS*2,
                              text=text)

                    if config.SHOW_TRACK:
                        for i in range(len(track.archive)):
                            if i != len(track.archive)-1:
                                c1 = get_b_center(track.archive[i],
                                                  config=config)
                                c2 = get_b_center(track.archive[i+1],
                                                  config=config)
                                cv2.line(frame,
                                         c1, c2,
                                         config.COLOR_BBOX_COUNTED,
                                         config.LINE_THICKNESS*2)

        for track in self.tracks:
            if len(track.archive):
                if config.SHOW_TRACK:

                    if track.miss_count:
                        COLOR_TRACK = config.COLOR_TRACK_BROKEN
                    else:
                        COLOR_TRACK = config.COLOR_TRACK

                    for i in range(len(track.archive)):
                        if i != len(track.archive)-1:
                            c1 = get_b_center(track.archive[i], config=config)
                            c2 = get_b_center(
                                track.archive[i+1], config=config)
                            cv2.line(frame, c1, c2, COLOR_TRACK, 2)

                    text = LABELS[track.label_i] + ' ' + \
                        '{:.2f}'.format(track.confidence)

                if config.SHOW_BBOX_PREV:

                    text = f"{LABELS[track.label_i]} {track.confidence:.2f}"

                    draw_bbox(frame,
                              bbox=track.archive[-1],
                              color=COLOR_TRACK,
                              text=text)

                if config.SHOW_BBOX_PREDICTED:

                    draw_bbox(frame,
                              bbox=track.bbox_predicted_last,
                              color=config.COLOR_BBOX_PREDICTED)

        if config.SHOW_BBOX:
            for bbox in bboxes:
                text = LABELS[bbox.get_label()] + ' ' + \
                    '{:.2f}'.format(bbox.c)

                draw_bbox(frame,
                          bbox=bbox,
                          color=config.COLOR_BBOX,
                          text=text)

        return frame

    @staticmethod
    def _interval_overlap(interval_a, interval_b):
        x1, x2 = interval_a
        x3, x4 = interval_b

        if x3 < x1:
            if x4 < x1:
                return 0
            else:
                return min(x2, x4) - x1
        else:
            if x2 < x3:
                return 0
            else:
                return min(x2, x4) - x3

    @staticmethod
    def bbox_iou(box1, box2):

        intersect_w = IOU_Tracker._interval_overlap([box1.xmin, box1.xmax],
                                                    [box2.xmin, box2.xmax])
        intersect_h = IOU_Tracker._interval_overlap([box1.ymin, box1.ymax],
                                                    [box2.ymin, box2.ymax])

        intersect = intersect_w * intersect_h

        w1, h1 = box1.xmax-box1.xmin, box1.ymax-box1.ymin
        w2, h2 = box2.xmax-box2.xmin, box2.ymax-box2.ymin

        union = w1*h1 + w2*h2 - intersect

        return float(intersect) / union
