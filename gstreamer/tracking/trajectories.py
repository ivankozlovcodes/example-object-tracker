import csv
import copy
import time
from tracking.trajectory import Trajectory, filter_by_timestamp, filter_by_frame_step, filter_by_frame_recall
from tracking.detected_object import DetectedObject

class ObjTrajectories:
  def __init__(self, cross_segment) -> None:
    self.trajectories = {}
    self._cross_clockwise_counter = 0
    self._cross_counter_clockwise_counter = 0
    self.cross_segment = cross_segment

  def load_csv(self, filename, debug=False, fieldnames=None):
    self.trajectories = {}
    with open(filename, 'r') as csvfile:
      if fieldnames is None:
        fieldnames = DetectedObject._fields
      reader = csv.DictReader(csvfile, fieldnames=fieldnames)
      next(reader, None)
      for row in reader:
        detected_object = DetectedObject.from_dict(row)
        if detected_object.id not in self.trajectories:
          self.trajectories[detected_object.id] = Trajectory(detected_object.id)
        self.trajectories[detected_object.id].add_object(detected_object)
        if self.cross_segment:
          clockwise, counter_clockwise =\
            self.trajectories[detected_object.id].detect_if_last_segment_crossed(self.cross_segment)
          self._cross_clockwise_counter += clockwise
          self._cross_counter_clockwise_counter += counter_clockwise
    if debug:
      self.print_debug_info()

  def get_trajectories_svg(self, drawing, start_time=0, end_time=None, track_ids=None, label=None, draw_last_rectangle=True, count_cross=True):
    FRAME_STEP = 5

    trajectories = copy.deepcopy(self.trajectories)
    if track_ids:
      trajectories = { key: value for key, value in trajectories.items() if key in track_ids }
    if label:
      trajectories = { key: value for key, value in trajectories.items() if value.average_label == label }
    clockwise_total, counter_clockwise_total = 0, 0
    for track_id, traj in trajectories.items():
      segments = traj.get_segments([
        filter_by_timestamp(start_time, end_time),
        # filter_by_frame_step(FRAME_STEP)
      ])
      if len(segments) == 0:
        continue
      color = traj.color
      self._update_swg_drawing_from_segments(drawing, segments, color)
      if draw_last_rectangle:
        _, (x, y) = segments[-1]
        point = traj.get_point_from_coords(x, y)
        drawing.add(drawing.rect(insert=(point.x, point.y), size=(point.w, point.h),
          fill='none', stroke=color, stroke_width='2'))
      if count_cross:
        (clockwise, counter_clockwise) = self._count_crosses_from_segments(segments)
        clockwise_total += clockwise
        counter_clockwise_total += counter_clockwise
    if count_cross:
      self._update_swg_drawimg_cross_segment(drawing)
      self._update_svg_drawing_cross_info(drawing, (clockwise_total, counter_clockwise_total))

  def _count_crosses_from_segments(self, segments):
    if self.cross_segment is None or len(segments) < 1:
      return (0, 0)
    clockwise_total = 0
    counter_clockwise_total = 0
    for segment in segments:
      (clockwise, counter_clockwise) = Trajectory.detect_cross(segment, self.cross_segment)
      clockwise_total += clockwise
      counter_clockwise_total += counter_clockwise
    return (clockwise_total, counter_clockwise_total)

  def _update_swg_drawimg_cross_segment(self, dwg):
    marker = dwg.marker(insert=(3, 3), size=(6,6))
    dwg.defs.add(marker)
    line = dwg.add(dwg.line(start=self.cross_segment[0], end=self.cross_segment[1], stroke='red', stroke_width='8'))
    line = dwg.add(dwg.line(start=self.cross_segment[0], end=self.cross_segment[1], stroke='blue', stroke_width='4'))
    marker.add(dwg.circle((3, 3), r=2, fill='red'))
    line.set_markers((marker, None, None))

  def _update_swg_drawing_from_segments(self, drawing, segments, color):
    for s in segments:
      p1, p2 = s
      if s is segments[0]:
        drawing.add(drawing.circle(center=p1, r=3, fill=color))
      drawing.add(drawing.line(start=p1, end=p2, stroke=color, stroke_width='3'))
      drawing.add(drawing.circle(center=p2, r=3, fill=color))

  def _update_svg_drawing_cross_info(self, drawing, counter):
    clockwise, counter_clockwise = counter
    width = int(drawing.attribs['width'])
    counter_message = 'In: {}. Out: {}'.format(clockwise, counter_clockwise)
    drawing.add(drawing.text(counter_message, insert=(width - 150, 30), fill='white', font_size=18, style='font-weight:bold;'))

  def print_debug_info(self):
    print('Total object detected {}'.format(len(self.trajectories.keys())))
    print('Total in: {}. Out: {}'.format(self._cross_clockwise_counter, self._cross_counter_clockwise_counter))
    people_detected = len(({ track_id: 1 for track_id, traj in self.trajectories.items() if traj.average_label == 'person' }).keys())
    print(f'{people_detected} people detected')
