
import sys
import gym
import numpy as np
sys.path.append("../")
from gym.spaces import Box
from ursina import Entity,Mesh,color,destroy
try:from library.myursina import Ursina
except:from ..library.myursina import Ursina
try:from library.frame import Frame
except:from ..library.frame import Frame
try:from library.ground import Ground
except:from ..library.ground import Ground
try:from library.bs import UAV_Base
except:from ..library.bs import UAV_Base
try:from library.mine import Advanced_Mine
except:from ..library.mine import Advanced_Mine
try:from library.target import Target
except:from ..library.target import Target
try:from library.uav import Fighter_UAV
except:from ..library.uav import Fighter_UAV
try:from library.reward import time_reward,live_uav_reward
except:from ..library.reward import time_reward,live_uav_reward
try:from library.constants import detection_range,distruction_range,max_uav_speed_dir,max_accleration,max_detection_range,mine_radar_range,target_height,target_clearence
except:from ..library.constants import detection_range,distruction_range,max_uav_speed_dir,max_accleration,max_detection_range,mine_radar_range,target_height,target_clearence
from .preprocessor import EnvStatePreprocessor
from panda3d.core import TransformState,RenderState

class UAV_sim(gym.Env):
    def __init__(self,length,bredth,max_height,max_time=500,
                 num_uav=10,num_mine=30,num_target=10,uavs_at_plane=4,
                 detection_range=detection_range,
                 distruction_range=distruction_range,
                 max_detection_range=max_detection_range,
                 max_uav_speed_dir=max_uav_speed_dir,
                 max_accleration=max_accleration,
                 mine_radar_range=mine_radar_range,
                 target_height=target_height,
                 target_clearence=target_clearence,
                 seed=None,same_config=False,
                 windowless=True,
                 draw_path=False):

        super().__init__()
        #TIME
        self.time=0
        self.max_time=max_time
        self.needreset=True
        self.paths=[]
        #ENV
        self.length=length
        self.bredth=bredth
        self.max_height=max_height
        #UAV_BASE
        self.uavs_at_plane=uavs_at_plane
        #UAV
        self.num_uav=num_uav
        self.detection_range=detection_range
        self.distruction_range=distruction_range
        self.max_detection_range=max_detection_range
        self.max_uav_speed_dir=max_uav_speed_dir
        self.max_accleration=max_accleration
        #MINE
        self.num_mine=num_mine
        self.mine_radar_range=mine_radar_range
        #TARGET
        self.num_target=num_target
        self.target_height=target_height
        self.target_clearence=target_clearence
        #SETUP
        self.seed=seed
        np.random.seed(self.seed)
        self.draw_path=draw_path
        self.same_config=same_config
        self.app=Ursina(windowless=windowless)
        self.env_state_preprocessor=EnvStatePreprocessor(self)
        self.frame=Frame(length=self.length,bredth=self.bredth,max_height=self.max_height)
        self.ground=Ground(length=self.length,bredth=self.bredth,max_height=self.max_height)
        self.uav_base=UAV_Base((self.length/2,-self.max_height/2,-self.bredth/2), self.length/10, self.bredth/10, self.max_height/2, self.num_uav,self.uavs_at_plane, self.mine_radar_range)
        self.uav_agents=self.uav_base.get_uav_agents()
        self._setup_objects()
        #SPACES
        self.action_space=Box(low=-1,high=1,shape=(self.num_uav*3,))
        self.observation_space=Box(low=-1,high=1,shape=(self.num_target*3+self.num_mine*3+self.num_uav*7,))

    def __repr__(self):
        return f"#UAV={self.num_uav}_"+f"max_speed={self.max_uav_speed_dir}_max_acc={self.max_accleration}_"+\
               f"detR={self.detection_range}_distR={self.distruction_range}_L={self.length}_B={self.bredth}_"+\
               f"H={self.max_height}_#Tar={self.num_target}_#Mine={self.num_mine}_MR={self.mine_radar_range}_"+\
               f"maxtime={self.max_time}_same_config={self.same_config}"

    def _setup_ground_obj_locs(self):
        self.ground_objs_locs=self.ground.get_target_and_mine_locs(self.num_target,self.target_clearence,self.num_mine,self.mine_radar_range)

    def _setup_objects(self):
        self._setup_ground_obj_locs()
        self.targets=[Target(t_loc,target_height=self.target_height) for t_loc in self.ground_objs_locs["targets"]] 
        self.mines=[Advanced_Mine(m_loc,mine_radar_range=self.mine_radar_range) for m_loc in self.ground_objs_locs["mines"]]
        self.uavs=dict([(Id,Fighter_UAV(Id,loc,self.frame.limits,
                                        distruction_range=self.distruction_range, 
                                        detection_range=self.detection_range, 
                                        max_uav_speed_dir=self.max_uav_speed_dir,
                                        max_detection_range=self.max_detection_range,
                                        max_accleration=self.max_accleration)) for Id,loc in zip(self.uav_agents,self.uav_base.uav_locs)])

    def _reset_objects(self,same_config):
        if same_config==False:
            self._setup_ground_obj_locs()
        i=0
        for t in self.targets:
            t.reset(self.ground_objs_locs["targets"][i])
            i+=1
        i=0
        for m in self.mines:
            m.reset(self.ground_objs_locs["mines"][i],self.mine_radar_range)
            i+=1

        for Id,u in self.uavs.items():
            u.reset(self.uav_base.uav_locs[Id],detection_range=self.detection_range,distruction_range=self.distruction_range)

    def _garbage_collect(self):
        TransformState.garbageCollect()
        RenderState.garbageCollect()

    def reset(self):
        self.time=0
        self.needreset=False
        if self.draw_path==True:self.remove_travel_path()
        self._garbage_collect()
        self._reset_objects(self.same_config)
        return self.get_state()

    def _env_state(self):
        state={"targets":[(t.position,t.status) for t in self.targets],
               "mines":[(m.position,m.status) for m in self.mines if m.status]}
        return state

    def _uav_state(self):
        uavs=[]
        for _,uav in self.uavs.items():
            uavs.append([uav.live,
                        uav.position.x/self.frame.limits["x"]["max"],
                        uav.position.y/self.frame.limits["y"]["max"],
                        uav.position.z/self.frame.limits["z"]["max"],
                        uav.velocity.x/uav.max_uav_speed_dir,
                        uav.velocity.y/uav.max_uav_speed_dir,
                        uav.velocity.z/uav.max_uav_speed_dir])
        return np.array(uavs,dtype="float32").flatten() #shape will be (num_uav x 7,)

    def get_state(self):
        env_state=self.env_state_preprocessor.preprocess(self._env_state()) #(num_target*3+num_mine*3,)
        uav_state=self._uav_state() #(num_uav*7,)
        return np.concatenate([env_state,uav_state])#(num_target*3+num_mine*3+num_uav*7,)

    def transform_action(self,acc_vec):
        """
        3d_acc_vec_id is continous -1 to 1
        acc: max and min is +- 10 m/s^2
        """
        max_acc=self.max_accleration #m/s^2
        acc_x,acc_y,acc_z=max_acc*acc_vec[0],max_acc*acc_vec[1],max_acc*acc_vec[2]
        return (acc_x,acc_y,acc_z,2*self.detection_range)

    def _step_on_uav(self,action): # action=Box((num_uav*3,))
        ##################### UAV ##########################################
        i=0
        uav_reward=0
        target_proximity_reward=0
        mine_proximity_reward=0
        num_live=0
        for _,uav in self.uavs.items():
            act=self.transform_action(action[i:i+3])
            uav_reward+=uav.agent_input(*act)
            target_proximity_reward+=uav.get_proximity_reward(self.targets,self.distruction_range,"target")
            mine_proximity_reward+=uav.get_proximity_reward(self.mines,self.mine_radar_range,"mine")
            if not uav.isDestroyed():
                num_live+=1
            i+=3

        uav_reward/=self.num_uav
        target_proximity_reward/=self.num_uav
        mine_proximity_reward/=self.num_uav
        alive_uav_reward=live_uav_reward(num_live,self.num_uav)

        ################### TARGET ########################################
        target_reward=0
        for t in self.targets:
            target_reward+=t.update()
        target_reward/=self.num_target

        ################## MINE ###########################################
        mine_reward=0
        for m in self.mines:
            mine_reward+=m.update()
        mine_reward/=self.num_mine

        ################# TIME ############################################
        self.time+=1
        t_reward=time_reward()
 
        reward=uav_reward+\
               target_proximity_reward+\
               mine_proximity_reward+\
               target_reward+\
               mine_reward+\
               t_reward+\
               alive_uav_reward

        return reward,num_live

    def step(self,action):
        assert self.needreset==False, "reset needed to simulate further"
        reward,num_live=self._step_on_uav(action)
        next_state=self.get_state()
        done,info=self.check_if_global_done(num_live)
        if done==True:
            info["stat"]=self.get_episode_stat(num_live)
            if self.draw_path==True:self.draw_travel_path()
            self.needreset=True
        return next_state,reward,done,info

    def draw_travel_path(self):
        for _,uav in self.uavs.items():
            self.paths.append(Entity(model=Mesh(vertices=uav.travel_path, mode='line', thickness=2), color=color.cyan))

    def remove_travel_path(self):
        for p in self.paths:
            destroy(p)
        self.paths=[]

    def check_if_global_done(self,num_live_uav):
        #pass num of live uavs
        global_done=True
        info={"reason":[]}
        for t in self.targets:
            if t.status=="operational":
                global_done=False
                break
        if global_done:info["reason"].append("all targets are down")
        if self.time>=self.max_time:
            global_done=True
            info["reason"].append("maximum time limit excided")
            if num_live_uav==0: info["reason"].append("all uavs are down")
        return global_done,info
    
    def get_episode_stat(self,num_live_uav):
        #pass num of live uavs
        num_live_targets=0;num_destroyed_targets=0
        for t in self.targets:
            if t.status=="operational":
                num_live_targets+=1
            elif t.status=="destroyed":
                num_destroyed_targets+=1
        num_live_mines=0;num_destroyed_mines=0
        for m in self.mines:
            if m.status=="found":
                num_live_mines+=1
            elif m.status=="destroyed":
                num_destroyed_mines+=1
        num_hidden_mines=self.num_mine-(num_live_mines+num_destroyed_mines)
        statistics={"num_live_uav":num_live_uav,
                    "num_live_targets":num_live_targets,
                    "num_hidden_mines":num_hidden_mines,
                    "num_destroyed_targets":num_destroyed_targets,
                    "num_live_mines":num_live_mines,
                    "num_destroyed_mines":num_destroyed_mines}
        return statistics

    def close(self):
        pass