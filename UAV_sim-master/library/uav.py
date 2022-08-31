from ursina import *
import numpy as np
try:from .radar import Radar
except:from radar import Radar
try:from .constants import max_detection_range,max_uav_speed_dir,distruction_range,detection_range,max_accleration
except:from constants import max_detection_range,max_uav_speed_dir,distruction_range,detection_range,max_accleration

class Fighter_UAV(Entity):
    def __init__(self,Id,position,limits=None,distruction_range=distruction_range,detection_range=detection_range,load_model=False,
                 max_uav_speed_dir=max_uav_speed_dir,max_detection_range=max_detection_range,max_accleration=max_accleration,**kwargs):
        super().__init__()
        self.Id=Id
        self.device='UAV'
        self.status="operational"
        if load_model==True:
            self.model="Assets/drone/Drone2"
        else:
            self.model="sphere"
        self.scale=Vec3(1,1,1)
        self.position=position
        self.limits=limits
        self.collider="sphere"
        self.color=color.light_gray
        self.velocity=Vec3(0,0,0)
        self.max_uav_speed_dir=max_uav_speed_dir
        self.max_detection_range=max_detection_range
        self.max_accleration=max_accleration
        self.distruction_radar=Radar(self, distruction_range, color=color.black33, device="distruction_radar")
        self.detection_radar=Radar(self, detection_range, color=color.black10, device="detection_radar")
        self.battery_lvl=100
        self.live=1
        for key,value in kwargs.items():
            setattr(self,key,value)

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

    def update_battery_lvl(self,accleration):
        """
        calculate deplition for self.velocity and accleration
        """
        deplition=0.1
        self.battery_lvl-=deplition

    def update_Scale(self,scale):
        self.detection_radar.scale_x=np.clip(scale,1,self.max_detection_range)
        self.detection_radar.scale_y=np.clip(scale,1,self.max_detection_range)
        self.detection_radar.scale_z=np.clip(scale,1,self.max_detection_range)

    def destroy(self):
        self.status="destroyed"
        self.detection_radar.visible=False
        self.distruction_radar.visible=False
        self.color=color.black50
        self.velocity=Vec3(0,0,0)
        self.detection_radar.scale=0
        self.battery_lvl=0
        self.live=0
        self.enabled=False
        #destroy(self)

    def isDestroyed(self):
        return self.status=="destroyed"

    def ifAttackedDistroy(self,types=['mine_radar','UAV']):
        hitinfo=self.intersects()
        for ent in hitinfo.entities:
            if ent.device==types[0]:
                ent.destroy() #mine
                self.destroy()#uav
            elif ent.device==types[1]:
                ent.destroy() #uav
                self.destroy() #uav

    def destruction_reward(self):
        if self.isDestroyed():
            return -1
        else:
            return 0

    def movement_reward(self):
        """implement this
        movement specific rewards"""
        reward=0
        return reward

    def transmission_reward(self):
        """implement this
        transmission power specific rewards"""
        reward=np.clip(1/self.detection_radar.scale_x,0,5)
        return reward

    def battery_failure_reward(self):
        if self.battery_lvl<0.01:
            self.destroy()
            return -1
        else:
            return 0

    def get_uav_reward(self):
        movement_reward=self.movement_reward()
        transmission_reward=self.transmission_reward()
        destroy_reward=self.destruction_reward()
        battery_failure_reward=self.battery_failure_reward()
        return movement_reward+transmission_reward+destroy_reward+battery_failure_reward

    def agent_input(self,acc_x,acc_y,acc_z,scale):
        if self.isDestroyed():
            return self.destruction_reward()
        accleration=Vec3(np.clip(acc_x,-self.max_accleration,self.max_accleration),
                         np.clip(acc_y,-self.max_accleration,self.max_accleration),
                         np.clip(acc_z,-self.max_accleration,self.max_accleration))
        self.update_battery_lvl(accleration)
        self.update_position_and_velocity(accleration)
        self.update_Scale(scale)
        self.ifAttackedDistroy()
        reward=self.get_uav_reward()
        return reward

    def get_neighbour_UAVs(self,type='UAV'):
        hitinfo=self.detection_radar.intersects()
        return [ent for ent in hitinfo.entities if ent.device==type]
    
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
            reward=self.agent_input(acc_x,acc_y,acc_z,scale)


if __name__=="__main__":
    app=Ursina()
    uav=Fighter_UAV(1,(0,0,0),None,10,20)
    EditorCamera()
    app.run()