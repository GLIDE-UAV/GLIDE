#%%
import numpy as np
from gym_wrapper.gymEnv import UAV_sim
uav_sim=UAV_sim(length=300, bredth=300, max_height=150)

#%%
global_done=False
curr_state=uav_sim.reset()
while not global_done:
    acts=uav_sim.sample_actions(curr_state)
    next_state,reward,notdones,(global_done,info)=uav_sim.step(acts)

    print(len(curr_state["uavs"]),len(acts),len(reward),len(next_state["uavs"]),len(notdones))
    if not global_done:curr_state=uav_sim.curr_state
print(info)
#%%
#END