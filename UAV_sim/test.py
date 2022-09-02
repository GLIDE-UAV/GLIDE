#%%
import time
from ursina import scene
from gym_wrapper.gymEnv import UAV_sim
#%%
def sample_trajectory():
    uav_sim=UAV_sim(length=300, bredth=300, max_height=150)
    print(uav_sim.observation_space.sample().shape)
    print('#entities before sampling: ',len(scene.entities))
    for _ in range(10000):
        t1=time.time()
        curr_state=uav_sim.reset()
        print("max,min=",curr_state.max(),curr_state.min())
        print('#entities after reset: ',len(scene.entities))

        done=False
        while not done:
            act=uav_sim.action_space.sample()
            next_state,reward,done,info=uav_sim.step(act)

        print(next_state.shape,reward)
        uav_sim.close()
        t2=time.time()
        print('#entities after close: ',len(scene.entities),"time taken to run",t2-t1)
    return info["reason"],info["stat"]
#%%
info,stat=sample_trajectory()
#%%
print(stat)
print(info)
#%%
#END