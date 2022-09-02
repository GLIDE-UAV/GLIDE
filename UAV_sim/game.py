from library.myursina import Ursina
from ursina import camera,EditorCamera
from library.constants import *
from library.frame import Frame
from library.ground import Ground
from library.bs import UAV_Base
from library.mine import Advanced_Mine
from library.target import Target
from library.uav import Fighter_UAV


if __name__=="__main__":
    app=Ursina()
    camera.set_position((0, 0, -588.445))

    #Eternals
    frame=Frame(length,bredth,max_height)
    ground=Ground(length,bredth,max_height)
    base=UAV_Base(base_position,base_length,base_bredth,base_height,num_of_uavs,uavs_at_plane,mine_radar_range)

    #game objects
    ground_objs_locs=ground.get_target_and_mine_locs(num_of_targets,target_clearence,num_of_mines,mine_radar_range)
    targets=[Target(t_loc,target_height) for t_loc in ground_objs_locs["targets"]]
    mines=[Advanced_Mine(m_loc,mine_radar_range) for m_loc in ground_objs_locs["mines"]]
    uavs=[Fighter_UAV(Id,u_loc,frame.limits,distruction_range,detection_range) for Id,u_loc in enumerate(base.uav_locs)]

    EditorCamera()
    app.run()