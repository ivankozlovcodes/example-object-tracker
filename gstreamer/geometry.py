def get_line_parameters(p1, p2):
    A = p1[1] - p2[1]
    B = p2[0] - p1[0]
    C = p1[0]*p2[1] - p2[0]*p1[1]
    return A, B, -C

def get_line_intersection(line1, line2):
    D  = line1[0] * line2[1] - line1[1] * line2[0]
    Dx = line1[2] * line2[1] - line1[1] * line2[2]
    Dy = line1[0] * line2[2] - line1[2] * line2[0]
    if D != 0:
        x = Dx / D
        y = Dy / D
        return x,y
    else:
        return None

def point_belong_to_segment(segment, point):
  ((x1, y1), (x2, y2)) = segment
  x3, y3 = point
  return (min(x1, x2) <= x3 <= max(x1, x2)) and (min(y1, y2) <= y3 <= max(y1, y2))

def segments_intersection(segment1, segment2):
  p1, p2 = segment1
  q1, q2 = segment2
  line1 = get_line_parameters(p1, p2)
  line2 = get_line_parameters(q1, q2)
  line_intersection = get_line_intersection(line1, line2)
  if line_intersection is not None and point_belong_to_segment(segment1, line_intersection) and point_belong_to_segment(segment2, line_intersection):
    return line_intersection
  return None

def point_to_segment_orientation(segment, point):
    """Returns True if `point` is clockwise oriented in regards of `segment`"""
    xp, yp = point
    ((x0, y0), (x1, y1)) = segment
    cross_product = (x1 - xp) * (y0 - yp) - (x0 - xp) * (y1 - yp)
    return cross_product > 0