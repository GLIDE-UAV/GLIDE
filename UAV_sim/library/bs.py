import numpy as np
from ursina import Entity,color
try:from .constants import mine_radar_range
except:from constants import mine_radar_range

class UAV_Base(Entity):
    def __init__(self,position,length,bredth,max_height,num_uav,uavs_at_plane=6,mine_radar_range=mine_radar_range):
        super().__init__()
        self.length=length
        self.bredth=bredth
        self.max_height=max_height

        self.model="wireframe_cube"
        self.color=color.orange
        self.scale=(length,max_height,bredth)
        self.position=(position[0]-self.length/2,position[1]+self.max_height/2,position[2]+self.bredth/2)
        self.limits=self.getLimits()

        self.num_uav=num_uav
        self.uavs_at_plane=uavs_at_plane
        self.mine_radar_range=mine_radar_range
        self.uav_locs=self.get_initial_uav_pos()

    def get_uav_agents(self):
        return [Id for Id in range(self.num_uav)]

    def getLimits(self):
        limits={
         "x":{"min":self.x-self.length//2,"max":self.x+self.length//2},
         "y":{"min":self.y-self.max_height//2,"max":self.y+self.max_height//2},
         "z":{"min":self.z-self.bredth//2,"max":self.z+self.bredth//2}
        }
        return limits

    def get_initial_uav_pos(self):
        dir_uav_count=int(self.uavs_at_plane//2)
        nostacks=int(np.ceil(self.num_uav/self.uavs_at_plane))

        x=np.linspace(self.limits["x"]["max"],self.limits["x"]["min"],dir_uav_count)
        z=np.linspace(self.limits["z"]["max"],self.limits["z"]["min"],dir_uav_count)
        y=np.linspace(self.limits["y"]["max"],self.limits["y"]["min"]+2*self.mine_radar_range,nostacks)

        X,Y,Z=np.meshgrid(x,y,z)
        X=X.flatten()
        Z=Z.flatten()
        Y=Y.flatten()
        return list(zip(X[:self.num_uav],Y[:self.num_uav],Z[:self.num_uav]))

    def isInside(self,obj):
        for dir in ["x","y","z"]:
            if (self.limits[dir]["min"]<=getattr(obj,dir)<=self.limits[dir]["max"])==False:
                return False
        return True


if __name__=="__main__":
    from myursina import Ursina
    from ursina import camera,EditorCamera
    app=Ursina()
    camera.set_position((0, 0, -230.337))
    bs=UAV_Base((10,10,0),10,10,5,5)
    EditorCamera()
    app.run()