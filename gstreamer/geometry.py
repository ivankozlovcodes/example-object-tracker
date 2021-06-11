def get_line_parameters(p1, p2):
    A = p1[1] - p2[1]
    B = p2[0] - p1[0]
    C = p1[0]*p2[1] - p2[0]*p1[1]
    return A, B, -C

def intersection(line1, line2):
    D  = line1[0] * line2[1] - line1[1] * line2[0]
    Dx = line1[2] * line2[1] - line1[1] * line2[2]
    Dy = line1[0] * line2[2] - line1[2] * line2[0]
    if D != 0:
        x = Dx / D
        y = Dy / D
        return x,y
    else:
        return None

def segments_intersection(section1, section2):
  p1, p2 = section1
  q1, q2 = section2
  line1 = get_line_parameters(p1, p2)
  line2 = get_line_parameters(q1, q2)
  return intersection(line1, line2)

def point_to_segment_orientation(segment, point):
    """Returns True if `point` is clockwise oriented in regards of `segment`"""
    xp, yp = point
    ((x0, y0), (x1, y1)) = segment
    cross_product = (x1 - xp) * (y0 - yp) * (x0 - xp) * (y1 - yp)
    return cross_product > 0