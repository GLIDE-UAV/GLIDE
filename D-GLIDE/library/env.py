import gym

class EnvWrapper(gym.Env):
    def __init__(self,env_obj):
        super().__init__()
        self.env=env_obj
        self.observation_space=self.env.observation_space
        self.action_space=self.env.action_space

    def __repr__(self):
        return self.env.__repr__()

    def reset(self):
        state=self.env.reset()
        return state

    def step(self,action):
        state,reward,done,info=self.env.step(action)
        return state,reward,done,info

    def close(self):
        self.env.close()

    
def make_env(UAV_sim, rank=0, args=None):
    def _init():
        env=EnvWrapper(UAV_sim(length=args.length,
                               bredth=args.bredth,
                               max_height=args.max_height,
                               max_time=args.max_time,
                               num_uav=args.num_uav,
                               num_mine=args.num_mine,
                               num_target=args.num_target,
                               uavs_at_plane=args.uavs_at_plane,
                               detection_range=args.detection_range,
                               distruction_range=args.distruction_range,
                               max_detection_range=args.max_detection_range,
                               max_uav_speed_dir=args.max_uav_speed_dir,
                               max_accleration=args.max_accleration,
                               mine_radar_range=args.mine_radar_range,
                               target_height=args.target_height,
                               target_clearence=args.target_clearence,
                               seed=args.seed+rank,
                               same_config=True if args.same_config=="True" else False,
                               windowless=True if args.windowless=="True" else False,
                               draw_path=True if args.draw_path=="True" else False))
        return env
    return _init

def _test(test_env,num=10,agent=None):
    cum_rewd=0
    cum_sim_time=0
    stat={"num_live_uav":0,"num_hidden_mines":0,
        "num_destroyed_targets":0,"num_live_mines":0,
        "num_destroyed_mines":0}
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
        cum_rewd+=rewd
        cum_sim_time+=sim_time
        for key in stat.keys():
            stat[key]+=info["stat"][key]
    test_env.close()
    avg_rewd=cum_rewd/num
    avg_sim_time=cum_sim_time/num
    for key in stat.keys():
            stat[key]/=num
    stat["avg_reward"]=avg_rewd
    stat["sim_time"]=avg_sim_time
    return stat