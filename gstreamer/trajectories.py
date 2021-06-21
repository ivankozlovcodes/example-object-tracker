import csv
import copy
import time
import hashlib
from collections import namedtuple, defaultdict
from geometry import segments_intersection, point_to_segment_orientation

DetectedObject = namedtuple('DetectedObject', 'id label x y w h cx cy score frame timestamp')

def id_to_random_color(number):
  numByte = str.encode(str(number))
  hashObj = hashlib.sha1(numByte).digest()
  r, g, b = hashObj[-1] % 255.0, hashObj[-2] % 255.0, hashObj[-3] % 255.0
  return int(r), int(g), int(b)

class ObjTrajectories:
  def __init__(self) -> None:
    self.objs_dict = defaultdict(lambda: [])
    self._cross_clockwise_counter = 0
    self._cross_counter_clockwise_counter = 0
    self.cross_segment = None
    self.start_time = None
    self._frame_number = 0

  def increment_frame_number(self):
    self._frame_number += 1

  def set_start_time(self):
    if self.start_time is None:
      self.start_time = time.monotonic()

  def set_cross_segment(self, src_w, src_h):
    self.cross_segment = (
      (src_w / 2, 0),
      (src_w / 2, src_h)
    )

  def update_obj_traj_dict(self, label, x, y, w, h, track_id, score):
    cx, cy = x + w / 2, y + h / 2
    timestamp = time.monotonic() - self.start_time
    detectedObject = DetectedObject(track_id, label, x, y, w, h, cx, cy, score, self._frame_number, timestamp)
    self.objs_dict[track_id].append(detectedObject)
    self._detect_if_object_has_crossed(track_id)

  def add_obj_traj_to_drawing(self, obj_id, drawing):
    prev_cx, prev_cy = None, None
    for box in self.objs_dict[obj_id]:
      color = 'rgb({},{},{})'.format(*id_to_random_color(obj_id))
      cx, cy = box.x + box.w / 2, box.y + box.h / 2
      drawing.circle(center=(cx, cy), r=3, fill=color)
      if prev_cx is not None:
        drawing.line(start=(prev_cx, prev_cy), end=(cx, cy), stroke=color, stroke_width='2')
      prev_cx, prev_cy = cx, cy

  def save_csv(self, filename):
    with open(filename, 'w') as csvfile:
      writer = csv.DictWriter(csvfile, fieldnames=DetectedObject._fields)
      writer.writeheader()
      for obj in self.objs_dict.values():
        for box in obj:
          writer.writerow(box._asdict())

  def load_csv(self, filename, debug=False):
    self.objs_dict = defaultdict(lambda: [])
    with open(filename, 'r') as csvfile:
      reader = csv.DictReader(csvfile, fieldnames=DetectedObject._fields)
      next(reader, None)
      for row in reader:
        row['id'] = int(row['id'])
        row['frame'] = int(row['frame'])
        row['x'] = float(row['x'])
        row['y'] = float(row['y'])
        row['w'] = float(row['w'])
        row['h'] = float(row['h'])
        row['cx'] = float(row['cx'])
        row['score'] = float(row['score'])
        row['timestamp'] = float(row['timestamp'])
        detectedObject = DetectedObject(**row)
        self.objs_dict[detectedObject.id].append(detectedObject)
    if debug:
      self.print_debug_info()

  def get_trajectories_svg(self, drawing, start_time=0, end_time=None, track_ids=None, draw_last_rectangle=True):
    if track_ids is not None:
      objects = { key: value for key, value in self.objs_dict.items() if key in track_ids}
    else:
      objects = copy.deepcopy(self.objs_dict)
    def filter_by_timestamp(box):
      after_start_time = box.timestamp >= start_time
      before_end_time = box.timestamp <= end_time if end_time is not None else True
      return after_start_time and before_end_time
    for track_id in objects.keys():
      boxes_filtered_by_timestamp = list(filter(filter_by_timestamp, objects[track_id]))
      FRAME_STEP = 5
      prev_frame_number = None
      boxes_filtered_by_frame_step = []
      for box in boxes_filtered_by_timestamp:
        if prev_frame_number is None or prev_frame_number + FRAME_STEP < box.frame:
          prev_frame_number = box.frame
          boxes_filtered_by_frame_step.append(box)
      objects[track_id] = boxes_filtered_by_frame_step
    objects = { key: value for key, value in objects.items() if len(value) > 0 }
    for track_id, points in objects.items():
      color = 'rgb({},{},{})'.format(*id_to_random_color(track_id))
      self._update_swg_drawing_from_points(drawing, points, color)
      if draw_last_rectangle:
        p = points[-1]
        drawing.add(drawing.rect(insert=(p.x, p.y), size=(p.w, p.h),
          fill='none', stroke=color, stroke_width='2'))

  def _detect_if_object_has_crossed(self, track_id):
    if self.cross_segment is None:
      return
    points = self.get_point_with_recall(track_id, frame_recall=5)
    segments = ObjTrajectories.build_segments_from_points(points)
    if len(segments) < 1:
      return
    last_segment = segments[-1]
    intersection = segments_intersection(last_segment, self.cross_segment)
    if intersection is not None:
      is_clockwise_intersection = point_to_segment_orientation(self.cross_segment, last_segment[1])
      if is_clockwise_intersection:
        self._cross_clockwise_counter += 1
      else:
        self._cross_counter_clockwise_counter += 1

  def get_point_with_recall(self, track_id, frame_recall):
    def recall_filter(point):
      return self._frame_number - frame_recall <= point.frame
    points = filter(recall_filter, self.objs_dict[track_id])
    return points

  def build_segments_from_points(points):
    prev_point_coords = None
    segments = []
    for p in points:
      if prev_point_coords is not None:
        segments.append((prev_point_coords, (p.cx, p.cy)))
      prev_point_coords = (p.cx, p.cy)
    return segments

  def update_swg_drawing(self, drawing):
    for track_id, obj in self.objs_dict.items():
      color = 'rgb({},{},{})'.format(*id_to_random_color(track_id))
      points = self.get_point_with_recall(track_id, frame_recall=5)
      self._update_swg_drawing_from_points(drawing, points, color)

  def _update_swg_drawing_from_points(self, drawing, points, color):
    segments = ObjTrajectories.build_segments_from_points(points)
    for s in segments:
      p1, p2 = s
      if s is segments[0]:
        drawing.add(drawing.circle(center=p1, r=3, fill=color))
      drawing.add(drawing.line(start=p1, end=p2, stroke=color, stroke_width='3'))
      drawing.add(drawing.circle(center=p2, r=3, fill=color))
    counter_message = 'Clockwise {}. Counterclockwise {}'.format(self._cross_clockwise_counter, self._cross_counter_clockwise_counter)
    drawing.add(drawing.text(counter_message, insert=(10, 10), fill='white', font_size=20))

  def print_debug_info(self):
    print('Total object detected {}'.format(len(self.objs_dict.keys())))
    print('Total clockwise clock {}. Counterclockwise {}'.format(self._cross_clockwise_counter, self._cross_counter_clockwise_counter))

ObjTrajectoriesSingletone = ObjTrajectories()
