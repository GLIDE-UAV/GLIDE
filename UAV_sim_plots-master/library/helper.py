import sys
sys.path.append("../")
sys.path.append("../PPO-UAV-sim/library/")
import constants as const
from algo import PPO2
from env import make_env
from UAV_sim.gym_wrapper.gymEnv import UAV_sim


class Args:
    def __init__(self,params):
        self.length=const.length
        self.bredth=const.bredth
        self.max_height=const.max_height
        self.max_time=const.max_time
        self.num_uav=params["num_uav"]
        self.num_mine=params["num_mine"]
        self.num_target=params["num_target"]
        self.uavs_at_plane=const.uavs_at_plane
        self.detection_range=const.detection_range
        self.distruction_range=const.distruction_range
        self.max_detection_range=const.max_detection_range
        self.max_uav_speed_dir=const.max_uav_speed_dir
        self.max_accleration=const.max_accleration
        self.mine_radar_range=const.mine_radar_range
        self.target_height=const.target_height
        self.target_clearence=const.target_clearence
        self.seed=const.seed
        self.same_config="False"
        self.windowless="True"
        self.draw_path="False"
    def __repr__(self):
        return str(self.__dict__)
    
def _test(test_env,num=10,agent=None):
    cum_rewd=[]
    cum_sim_time=[]
    stat={"num_live_uav":[],"num_hidden_mines":[],
        "num_destroyed_targets":[],"num_live_mines":[],
        "num_destroyed_mines":[]}
    for _ in range(num):
        done=False
        rewd=0
        sim_time=0
        curr_state=test_env.reset()
        while not done:
            act,_=agent.predict(curr_state)
            next_state,r,done,info=test_env.step(act)
            curr_state=next_state
            rewd+=r
            sim_time+=1
        cum_rewd.append(rewd)
        cum_sim_time.append(sim_time)
        for key in stat.keys():
            stat[key].append(info["stat"][key])
    test_env.close()
    avg_rewd=sum(cum_rewd)/num
    avg_sim_time=sum(cum_sim_time)/num
    stat["reward"]=cum_rewd
    stat["sim_time"]=cum_sim_time
    stat["avg_reward"]=avg_rewd
    stat["avg_sim_time"]=avg_sim_time
    return stat

def evaluate(uav_exp,mode="dis",exp_name="uav5",num_test=10):
    env=make_env(UAV_sim,10,Args(uav_exp[exp_name]))()
    model_name= exp_name if mode=="dis" else exp_name+"_cent"
    model=PPO2.load(f"../PPO-UAV-sim/model/{model_name}_ppo")
    res=_test(env,num_test,model)
    return res