import hashlib
from functools import reduce
from collections import defaultdict

from geometry import segments_intersection, point_to_segment_orientation

PERSON_DETECTION_THRESHOLD = 0.3

def filter_by_frame_recall(frame_recall):
  def recall_filter(point):
    return self._frame_number - frame_recall <= point.frame
  return recall_filter

def filter_by_frame_step(frame_step):
  prev_frame_number = None
  def fn(point):
    nonlocal prev_frame_number
    if prev_frame_number is None or prev_frame_number + frame_step < point.frame:
      prev_frame_number = point.frame
      return True
    return False
  return fn

def filter_by_timestamp(start_time, end_time):
  def fn(point):
    after_start_time = point.timestamp >= start_time
    before_end_time = point.timestamp <= end_time if end_time is not None else True
    return after_start_time and before_end_time
  return fn

def id_to_random_color(number):
  numByte = str.encode(str(number))
  hashObj = hashlib.sha1(numByte).digest()
  r, g, b = hashObj[-1] % 255.0, hashObj[-2] % 255.0, hashObj[-3] % 255.0
  return int(r), int(g), int(b)

class Trajectory:
  def __init__(self, track_id):
    self.track_id = track_id
    self.points = []
    self.color = 'rgb({},{},{})'.format(*id_to_random_color(track_id))

  def add_object(self, detected_object):
    self.points.append(detected_object)

  @property
  def average_label(self):
    labels_dict = defaultdict(lambda: 0)
    for point in self.points:
      labels_dict[point.label] += point.score
    peson_fraction = labels_dict['person'] / sum(labels_dict.values())
    if peson_fraction >= PERSON_DETECTION_THRESHOLD:
      return 'person'
    dominant_label = max(labels_dict, key=labels_dict.get)
    return dominant_label

  def get_points_filtered(self, filters=[]):
    points = self.points
    for filter_fn in filters:
      points = list(filter(filter_fn, points))
    return points

  def get_segments(self, filters=None):
    points = self.points if filters is None else self.get_points_filtered(filters)
    return self._build_segments_from_points(points)

  def detect_if_last_segment_crossed(self, cross_segment):
    segments = self.get_segments()
    if len(segments) > 0:
      return Trajectory.detect_cross(segments[-1], cross_segment)
    return (0, 0)

  def _build_segments_from_points(self, points):
    prev_point_coords = None
    segments = []
    for p in points:
      if prev_point_coords is not None:
        segments.append((prev_point_coords, (p.cx, p.cy)))
      prev_point_coords = (p.cx, p.cy)
    return segments

  def detect_cross(segment, cross_segment):
    if segments_intersection(segment, cross_segment):
      _, end_point = segment
      is_clockwise_intersection = point_to_segment_orientation(cross_segment, end_point)
      return (+is_clockwise_intersection, +(not is_clockwise_intersection))
    return (0, 0)

  def get_point_from_coords(self, x, y):
    for p in self.points:
      if p.cx == x and p.cy == y:
        return p
    return None
