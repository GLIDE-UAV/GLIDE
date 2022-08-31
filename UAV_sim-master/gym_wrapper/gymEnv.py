
import sys
import gym
import numpy as np
sys.path.append("../")
from ursina import Ursina
try:from library.frame import Frame
except:from ..library.frame import Frame
try:from library.ground import Ground
except:from ..library.ground import Ground
try:from library.mine import Advanced_Mine
except:from ..library.mine import Advanced_Mine
try:from library.target import Target
except:from ..library.target import Target
try:from library.uav import Fighter_UAV
except:from ..library.uav import Fighter_UAV

class UAV_sim(gym.Env):
    def __init__(self,length,bredth,max_height,max_time=500,
                 num_uav=10,num_mine=30,num_target=10):

        super().__init__()
        #TIME
        self.time=0
        self.max_time=max_time
        self.needreset=True
        #ENV
        self.length=length
        self.bredth=bredth
        self.max_height=max_height
        #UAV
        self.num_uav=num_uav
        #MINE
        self.num_mine=num_mine
        #TARGET
        self.num_target=num_target
        #SETUP
        self.past_queue=[]
        self.app=Ursina()
        self.frame=Frame(length=self.length,bredth=self.bredth,max_height=self.max_height)
        self.ground=Ground(length=self.length,bredth=self.bredth,max_height=self.max_height)

    def reset(self):
        self.time=0
        self.needreset=False
        self.targets=[Target(self.ground.getRandomLoc(self.ground.limits["y"]["min"])) for _ in range(self.num_target)]
        self.mines=[Advanced_Mine(self.ground.getRandomLoc(self.ground.limits["y"]["min"])) for _ in range(self.num_mine)]
        self.uavs=dict([(Id,Fighter_UAV(Id,self.ground.getRandomLoc(0),self.frame.limits)) for Id in range(self.num_uav)])
        return self.curr_state
    
    @property
    def curr_state(self):
        state={"targets":[(t.position,t.status) for t in self.targets],
               "mines":[(m.position,m.status) for m in self.mines if m.status in ["found","destroyed"]]}
        uavs=[]
        self.past_queue=[]
        for Id,uav in self.uavs.items():
            if not uav.isDestroyed():
                self.past_queue.append(Id)
                uavs.append((uav.live,
                            uav.position.x/self.frame.limits["x"]["max"],uav.position.y/self.frame.limits["y"]["max"],uav.position.z/self.frame.limits["z"]["max"],
                            uav.velocity.x/uav.max_uav_speed_dir,uav.velocity.y/uav.max_uav_speed_dir,uav.velocity.z/uav.max_uav_speed_dir,
                            uav.detection_radar.scale_x/uav.max_detection_range,
                            uav.battery_lvl/100))
        state["uavs"]=uavs
        return state

    def __next_state(self):
        state={"targets":[(t.position,t.status) for t in self.targets],
               "mines":[(m.position,m.status) for m in self.mines if m.status in ["found","destroyed"]]}
        uavs=[];dones=[]
        for Id in self.past_queue:
            uav=self.uavs[Id]
            dones.append(uav.isDestroyed())
            uavs.append((uav.live,
                        uav.position.x/self.frame.limits["x"]["max"],uav.position.y/self.frame.limits["y"]["max"],uav.position.z/self.frame.limits["z"]["max"],
                        uav.velocity.x/uav.max_uav_speed_dir,uav.velocity.y/uav.max_uav_speed_dir,uav.velocity.z/uav.max_uav_speed_dir,
                        uav.detection_radar.scale_x/uav.max_detection_range,
                        uav.battery_lvl/100))
        state["uavs"]=uavs
        return state,dones

    def step_actions(self,action_arr):#[(acc_x,acc_y,acc_z,scale),...]
        self.time+=1
        uav_rewards=[]
        for Id,act in zip(self.past_queue,action_arr):
            uav_reward=self.uavs[Id].agent_input(*act)
            uav_rewards.append(uav_reward)
        global_reward=0
        for t in self.targets:
            global_reward+=t.update()
        for m in self.mines:
            global_reward+=m.update()
        reward=np.array(uav_rewards)+global_reward
        return reward

    def transform_action(self,acc_vec_id,detection_range=20): #detection range=20m
        """
        3d_acc_vec_id is 0->124 nums (5x5x5) cube positions
        acc: in 1 to 5 levels{-5m/sec2,-2.5m/sec2,0m/sec2,2.5m/sec2,5m/sec2}
        """
        acc_x_id,acc_y_id,acc_z_id=((acc_vec_id//5)//5)%5,(acc_vec_id//5)%5,acc_vec_id%5
        map={0:-5,1:-2.5,2:0,3:2.5,4:5} #acc_dir_id to m/see2
        return (map[acc_x_id],map[acc_y_id],map[acc_z_id],detection_range)

    def convert_action_arr(self,actions):#[1,0,124,56,...]
        converted_actions=[]
        for act in actions:
            converted_actions.append(self.transform_action(act))
        return converted_actions #[(acc_x,acc_y,acc_z,scale),...]

    def checkIfGlobalDone(self,state):
        global_done=True
        info={"reason":[]}
        for t in state["targets"]:
            if t[1]=="operational":
                global_done=False
                break
        if global_done: info["reason"].append("all targets are down")
        if len([u for u in state["uavs"] if u[0]==1])==0:
            global_done=True
            info["reason"].append("all uavs are down")
        if self.time>=self.max_time:
            global_done=True
            info["reason"].append("max_time reached")
        if global_done:
            del self.targets
            del self.mines
            del self.uavs
            self.needreset=True
        return global_done,info

    def step(self,actions): #[1,2,0,124,12....]
        assert self.needreset==False, "reset needed to simulate further"
        converted_actions=self.convert_action_arr(actions)
        reward=self.step_actions(converted_actions)
        next_state,dones=self.__next_state()
        global_done,info=self.checkIfGlobalDone(next_state)
        if global_done:
            dones_len=len(dones)
            dones=[True]*dones_len
        notdones=[not d for d in dones]
        return next_state,reward,notdones,(global_done,info)

    def sample_action(self):
        """action_space- 5x5x5"""
        return np.random.randint(0,125)

    def sample_actions(self,state):
        num_uavs=len(state["uavs"])
        actions=[self.sample_action() for _ in range(num_uavs)]
        return actions