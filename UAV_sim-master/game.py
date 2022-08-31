from ursina import *
from library.constants import *
from library.frame import Frame
from library.ground import Ground
from library.mine import Advanced_Mine
from library.target import Target
from library.uav import Fighter_UAV


if __name__=="__main__":
    app=Ursina()
    camera.set_position(Vec3(0, 0, -588.445))

    frame=Frame(length,bredth,max_height)
    ground=Ground(length,bredth,max_height)
    targets=[Target(ground.getRandomLoc(ground.limits["y"]["min"]),load_model=load_model) for _ in range(num_of_targets)]
    mines=[Advanced_Mine(ground.getRandomLoc(ground.limits["y"]["min"]),
                         mine_radar_range) for _ in range(num_of_mines)]

    uavs=[Fighter_UAV(_,
                      ground.getRandomLoc(0),
                      frame.limits,
                      distruction_range,
                      detection_range,
                      load_model) for _ in range(num_of_uavs)]
    EditorCamera()
    app.run()