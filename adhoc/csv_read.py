import svgwrite
from tracking.trajectories import ObjTrajectories

fieldnames = 'id label x y w h cx cy score frame timestamp'.split(' ')
src_size = (640, 480)
p2 = (285.0, 270.0)
p1 = (290.0, 0)

cross_segment = (p1, p2)
obj_trajectories = ObjTrajectories(cross_segment)

obj_trajectories.load_csv('/home/ivan/projects/example-object-tracker/assets/people_walking_standing_1080p.csv', fieldnames=fieldnames, debug=True)

dwg = svgwrite.Drawing('test.svg', size=src_size)
obj_trajectories.get_trajectories_svg(dwg, start_time=10, end_time=40, label='person', count_cross=True)
dwg.save()
