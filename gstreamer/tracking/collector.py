import time
import pandas as pd

from tracking.detected_object import DetectedObject

class Collector:
  def __init__(self):
    self.reset()

  def increment_frame_number(self):
    self._frame_number += 1

  def reset(self):
    self.points = pd.Dataframe(columns=DetectedObject._fields)
    self._frame_number = 0
    self._start_time = None

  def start(self):
    if self._start_time is None:
      self._start_time = time.monotonic()

  def add_point(label, x, y , w, h, track_id, score):
    timestamp = timestamp = time.monotonic() - self._start_time
    detectedObject = DetectedObject(track_id, label, x, y, w, h, score, self._frame_number, timestamp)
    self.points.append(detectedObject._asdict())

  def dump(filename):
    self.points.to_csv(filename)

CollectorSingletone = Collector()
