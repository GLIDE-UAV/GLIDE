import numpy as np
from tensorflow.keras.preprocessing.sequence import pad_sequences

class LinearScale:
    def __init__(self,min_=0,max_=79,MIN=0,MAX=300):
        self.min_=min_
        self.max_=max_
        self.MIN=MIN
        self.MAX=MAX
    def convert(self,val):
        return (((val-self.MIN)/(self.MAX-self.MIN))*(self.max_-self.min_))+self.min_
    
def draw_circle(x,y,length,bredth,size=1.5):
    center=[x,y]
    Y, X = np.ogrid[:length, :bredth]
    dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1])**2)
    mask = dist_from_center <= size
    return mask.astype(np.int32)

class Preprocessor:
    def __init__(self,env,pix):
        self.length=env.length
        self.bredth=env.bredth
        self.num_uav=env.num_uav
        self.pix=pix
        
        self.scale=LinearScale(min_=0,max_=self.pix,MIN=0,MAX=self.length)
        self.get_loc=lambda pos:[round(pos.x)+(self.length//2),round(pos.z)+(self.bredth//2)]
        
    def preprocess(self,state,padding=False):
        target_channel=np.zeros((self.pix,self.pix))
        mine_channel=np.zeros((self.pix,self.pix))
        #targets
        for t in state["targets"]:
            x,y=self.get_loc(t[0])
            x=self.scale.convert(x)
            y=self.scale.convert(y)
            if t[1]=="operational":
                target_channel+=draw_circle(x,y,self.pix,self.pix)*+1
            if t[1]=="destroyed":
                target_channel+=draw_circle(x,y,self.pix,self.pix)*-1
        #mines
        for m in state["mines"]:
            x,y=self.get_loc(m[0])
            x=self.scale.convert(x)
            y=self.scale.convert(y)
            if m[1]=="found":
                mine_channel+=draw_circle(x,y,self.pix,self.pix)*+1
            if m[1]=="destroyed":
                mine_channel+=draw_circle(x,y,self.pix,self.pix)*-1
        #uavs       
        series=[]
        for pid,p_uav in enumerate(state["uavs"]):
            seq=[]
            for sid,s_uav in enumerate(state["uavs"]):
                if sid==pid:continue
                seq.append([*s_uav])
            seq.append([*p_uav])
            series.append(np.array(seq))
        uav_series=np.array(series,dtype="float32")
        #padding if required
        if padding==True:uav_series=pad_sequences(uav_series,maxlen=self.num_uav,dtype='float32')
        images=np.array([np.concatenate((target_channel.reshape(self.pix,self.pix,1),
                                         mine_channel.reshape(self.pix,self.pix,1)),axis=2)]*len(state["uavs"]),dtype="float32")
        return images,uav_series