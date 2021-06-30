import csv
import time

from tracking.detected_object import DetectedObject

class Collector:
  def __init__(self):
    self.reset()

  def increment_frame_number(self):
    self._frame_number += 1

  def reset(self):
    self.points = []
    self._frame_number = 0
    self._start_time = None

  def start(self):
    if self._start_time is None:
      self._start_time = time.monotonic()

  def add_point(self, label, x, y , w, h, track_id, score):
    timestamp = timestamp = time.monotonic() - self._start_time
    self.points.append(
      DetectedObject(track_id, label, x, y, w, h, score, self._frame_number, timestamp)
    )

  def dump(self, filename):
    with open(filename, 'w') as csvfile:
      writer = csv.DictWriter(csvfile, fieldnames=DetectedObject._fields)
      writer.writeheader()
      for point in self.points:
        writer.writerow(point._asdict())

CollectorSingletone = Collector()
