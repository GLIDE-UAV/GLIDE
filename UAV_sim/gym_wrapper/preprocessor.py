import numpy as np

class EnvStatePreprocessor:
    def __init__(self,env):
        self.length=env.length
        self.bredth=env.bredth
        self.num_uav=env.num_uav
        
    def preprocess(self,state):
        target_channel=[]
        mine_channel=[]
        #targets
        for t in state["targets"]:
            x,y=(t[0].x/(self.length//2)),(t[0].z/(self.bredth//2))
            if t[1]=="operational":
                target_channel.extend([x,y,1.])
            if t[1]=="destroyed":
                target_channel.extend([x,y,0.])
        #mines
        for m in state["mines"]:
            x,y=(m[0].x/(self.length//2)),(m[0].z/(self.bredth//2))
            if m[1]=="found":
                mine_channel.extend([x,y,1.])
            if m[1]=="destroyed":
                mine_channel.extend([x,y,0.])
            if m[1]=="hidden":
                mine_channel.extend([-1.,-1.,1.])

        arr=np.array(target_channel+mine_channel,dtype="float32")
        return arr