import numpy as np
from ursina import Entity

class Ground(Entity):
    def __init__(self,length,bredth,max_height):
        super().__init__()
        self.length=length
        self.bredth=bredth
        self.max_height=max_height

        self.model="plane"
        self.texture="grass"
        self.scale=(length,0,bredth)
        self.position=(0,-max_height//2,0)
        self.limits=self.getLimits()

    def getLimits(self):
        limits={
         "x":{"min":-self.length//2,"max":self.length//2},
         "z":{"min":-self.bredth//2,"max":self.bredth//2}
        }
        return limits

    def get_target_and_mine_locs(self,num_targets,target_clearence,num_mines,mine_radar_range):
        target_locs=[(np.random.uniform(self.limits["x"]["min"],self.limits["x"]["max"]),self.y,
                      np.random.uniform(self.limits["z"]["min"],self.limits["z"]["max"])) for _ in range(num_targets)]
        m=0
        looped=0
        mine_locs=[]
        while m<num_mines:
            candidate_mine_loc=(np.random.uniform(self.limits["x"]["min"],self.limits["x"]["max"]),self.y,
                                np.random.uniform(self.limits["z"]["min"],self.limits["z"]["max"]))
            for t_loc in target_locs:
                if euclidean(candidate_mine_loc,t_loc)<mine_radar_range+target_clearence:
                    break
            else:
                mine_locs.append(candidate_mine_loc)
                m+=1

            looped+=1
            if looped>4*num_mines:
                raise Exception("Not enough space in ground to accomodate all mines!")

        return dict(targets=target_locs,mines=mine_locs)


def euclidean(a,b):
    return np.sqrt(np.square(a[0]-b[0])+np.square(a[1]-b[1])+np.square(a[2]-b[2]))



if __name__=="__main__":
    from myursina import Ursina
    from ursina import EditorCamera
    app=Ursina()
    ground=Ground(100,100,50)
    locs=ground.get_target_and_mine_locs(10,2,20,5)
    print(len(locs["targets"]),len(locs["mines"]))
    print(locs)
    EditorCamera()
    app.run()