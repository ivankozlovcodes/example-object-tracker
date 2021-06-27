import svgwrite
from tracking.trajectories import ObjTrajectoriesSingletone

fieldnames = 'id label x y w h cx cy score frame timestamp'.split(' ')
src_size = (640, 480)
p2 = (285.0, 270.0)
p1 = (290.0, 0)
ObjTrajectoriesSingletone.set_cross_segment(p1, p2)
ObjTrajectoriesSingletone.load_csv('./people_walking_standing_1080p.csv', fieldnames=fieldnames, debug=True)
dwg = svgwrite.Drawing('test.svg', size=src_size)
# ObjTrajectoriesSingletone.get_trajectories_svg(dwg, start_time=38, end_time=40, label='person', count_cross=True)
track_ids = [
  44,
]
ObjTrajectoriesSingletone.get_trajectories_svg(dwg, start_time=10, end_time=12, track_ids=track_ids, label='person', count_cross=True, draw_last_rectangle=True)
dwg.save()
# print(dwg.tostring())