from collections import namedtuple

DetectedObjectTuple = namedtuple('DetectedObject', 'id label x y w h score frame timestamp')

class DetectedObject(DetectedObjectTuple):
  @property
  def cx(self):
    return self.x + self.w / 2
  
  @property
  def cy(self):
    return self.y + self.h / 2

  @staticmethod
  def from_dict(d):
    d['id'] = int(d['id'])
    d['frame'] = int(d['frame'])
    d['x'] = float(d['x'])
    d['y'] = float(d['y'])
    d['w'] = float(d['w'])
    d['h'] = float(d['h'])
    d['score'] = float(d['score'])
    d['timestamp'] = float(d['timestamp'])
    # todo: remove
    del d['cx']
    del d['cy']
    return DetectedObject(**d)
