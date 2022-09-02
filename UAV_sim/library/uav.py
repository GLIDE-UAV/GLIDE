import numpy as np
try:from .radar import Radar
except:from radar import Radar
from ursina import Entity,color,destroy,held_keys,Vec3
try:from .reward import uav_destroy,nothing,Proximity
except:from reward import uav_destroy,nothing,Proximity
try:from .constants import max_detection_range,max_uav_speed_dir,distruction_range,detection_range,max_accleration
except:from constants import max_detection_range,max_uav_speed_dir,distruction_range,detection_range,max_accleration

class Fighter_UAV(Entity):
    def __init__(self,Id,position,limits=None,distruction_range=distruction_range,detection_range=detection_range,
                 max_uav_speed_dir=max_uav_speed_dir,max_detection_range=max_detection_range,max_accleration=max_accleration):
        super().__init__()
        self.Id=Id
        self.device='UAV'
        self.travel_path=[]

        self.model="sphere"
        self.collider="sphere"
        self.color=color.light_gray
        self.scale=(1,1,1)
        self.position=position
        self.velocity=Vec3(0,0,0)
        self.limits=limits
        
        self.max_uav_speed_dir=max_uav_speed_dir
        self.max_detection_range=max_detection_range
        self.max_accleration=max_accleration

        self.status="operational"
        self.battery_lvl=100
        self.enabled=True
        self.live=1

        self.distruction_radar=Radar(self, distruction_range, color=color.black33, device="distruction_radar")
        self.detection_radar=Radar(self, detection_range, color=color.black10, device="detection_radar")

    def track_pos(self,reset=False):
        if reset==True:
            self.travel_path=[]
        self.travel_path.append((self.x,self.y,self.z))

    def reset(self,position,detection_range,distruction_range):
        self.position=position
        self.status="operational"
        self.track_pos(reset=True)
        self.detection_radar.reset(detection_range)
        self.distruction_radar.reset(distruction_range)
        self.velocity=Vec3(0,0,0)
        self.battery_lvl=100
        self.enabled=True
        self.live=1

    def get_bounded_position_and_collision(self,next_position):
        collision={"x":False,"y":False,"z":False}
        if self.limits==None:
            return next_position,collision
        if (self.limits["x"]["min"]<=next_position[0]<=self.limits["x"]["max"])==False:
            next_position[0]=np.clip(next_position[0],self.limits["x"]["min"],self.limits["x"]["max"])
            collision["x"]=True
        if (self.limits["y"]["min"]<=next_position[1]<=self.limits["y"]["max"])==False:
            next_position[1]=np.clip(next_position[1],self.limits["y"]["min"],self.limits["y"]["max"])
            collision["y"]=True
        if (self.limits["z"]["min"]<=next_position[2]<=self.limits["z"]["max"])==False:
            next_position[2]=np.clip(next_position[2],self.limits["z"]["min"],self.limits["z"]["max"])
            collision["z"]=True
        return next_position,collision
    
    def expected_velocity(self,accleration,dt=1):
        vel=self.velocity+(accleration*dt)
        vel[0]=np.clip(vel[0],-self.max_uav_speed_dir,self.max_uav_speed_dir)
        vel[1]=np.clip(vel[1],-self.max_uav_speed_dir,self.max_uav_speed_dir)
        vel[2]=np.clip(vel[2],-self.max_uav_speed_dir,self.max_uav_speed_dir)
        return vel

    def update_position(self,expected_vel,dt=1):
        move=((self.velocity+expected_vel)/2)*dt
        bounded_position,collision=self.get_bounded_position_and_collision(self.position+move)
        self.set_position(bounded_position)
        self.track_pos(reset=False)
        return collision

    def update_velocity(self,collision,expected_vel):
        if collision["x"]==True:
            expected_vel[0]=0.
        if collision["y"]==True:
            expected_vel[1]=0.
        if collision["z"]==True:
            expected_vel[2]=0.
        self.velocity=expected_vel

    def update_position_and_velocity(self,accleration,dt=1):
        expected_vel=self.expected_velocity(accleration,dt)
        collision=self.update_position(expected_vel,dt)
        self.update_velocity(collision,expected_vel)

    def update_Scale(self,scale):
        if self.detection_radar.scale_x==scale:
            return
        self.detection_radar.scale_x=np.clip(scale,1,2*self.max_detection_range)
        self.detection_radar.scale_y=np.clip(scale,1,2*self.max_detection_range)
        self.detection_radar.scale_z=np.clip(scale,1,2*self.max_detection_range)

    def update_battery_lvl(self,accleration):
        pass

    def destroy(self):
        self.status="destroyed"
        self.detection_radar.destroy()
        self.distruction_radar.destroy()
        self.velocity=Vec3(0,0,0)
        self.battery_lvl=0
        self.enabled=False
        self.live=0

    def deAllocate(self):
        destroy(self.detection_radar)
        destroy(self.distruction_radar)
        destroy(self)

    def isDestroyed(self):
        return self.status=="destroyed"

    def ifAttackedDistroy(self,types=['mine_radar','UAV']):
        hitinfo=self.intersects()
        for ent in hitinfo.entities:
            if hasattr(ent,"device")==False:
                continue
            elif ent.device==types[0]:
                ent.parent.destroy()
                self.destroy()
            elif ent.device==types[1]:
                avoid_distance=-self.position.normalized()*2
                self.set_position(self.position+avoid_distance)

    def destruction_reward(self):
        return uav_destroy() if self.isDestroyed() else nothing()

    def movement_reward(self):
        reward=0
        return reward

    def transmission_reward(self):
        reward=0
        return reward

    def battery_failure_reward(self):
        reward=0
        return reward

    def get_uav_reward(self):
        destroy_reward=self.destruction_reward()
        return destroy_reward

    def agent_input(self,acc_x,acc_y,acc_z,scale):
        if self.isDestroyed():
            return nothing()
        accleration=Vec3(np.clip(acc_x,-self.max_accleration,self.max_accleration),
                         np.clip(acc_y,-self.max_accleration,self.max_accleration),
                         np.clip(acc_z,-self.max_accleration,self.max_accleration))
        self.update_battery_lvl(accleration)
        self.update_position_and_velocity(accleration)
        self.update_Scale(scale)
        self.ifAttackedDistroy()
        reward=self.get_uav_reward()
        return reward

    def distance(self,other):
        diff=(self.position-other.position)
        return (diff.x**2+diff.y**2+diff.z**2)**0.5

    def find_min_distance(self,list_objs):
        min_dis=np.inf
        for obj in list_objs:
            if obj.isDestroyed():continue
            dis=self.distance(obj)
            if dis<min_dis:
                min_dis=dis
        return min_dis

    def get_proximity_reward(self,list_objs,least_distance,type="mine"):
        if self.isDestroyed() or len(list_objs)==0:
            return nothing()
        min_distance=self.find_min_distance(list_objs)
        if type=="mine":
            return Proximity.mine_reward(min_distance,least_distance)
        elif type=="target":
            return Proximity.target_reward(min_distance,least_distance)
        else:
            raise Exception("invalid object type! should be mine or target")
    
    def input(self,event):
        if event in ['a','d','w','s','q','x','e','r'] and self.status=="operational":
            acc_delta=1;scale_delta=5
            """
            left: a
            right: d
            forward: w
            backward: s
            up: q
            down: x
            expand: e
            srink: r
            """
            acc_x=acc_delta*(held_keys['d']-held_keys['a'])
            acc_z=acc_delta*(held_keys['w']-held_keys['s'])
            acc_y=acc_delta*(held_keys["q"]-held_keys["x"])
            scale=self.detection_radar.scale_x
            if held_keys["e"]:
                scale+=scale_delta
            elif held_keys["r"]:
                scale-=scale_delta
            self.agent_input(acc_x,acc_y,acc_z,scale)


if __name__=="__main__":
    from myursina import Ursina
    from ursina import EditorCamera
    app=Ursina()
    uav=Fighter_UAV(1,(0,0,0),None,10,20)
    EditorCamera()
    app.run()