from ursina import *
import numpy as np

class Ground(Entity):
    def __init__(self,length,bredth,max_height,**kwargs):
        super().__init__()
        self.length=length
        self.bredth=bredth
        self.max_height=max_height

        self.parent=scene
        self.model="plane"
        self.scale=Vec3(length,0,bredth)
        self.position=Vec3(0,-max_height//2,0)
        self.texture="grass"
        self.limits=self.getLimits()
        for key,value in kwargs.items():
            setattr(self,key,value)

    def getLimits(self):
        limits={
         "x":{"min":-self.length//2,"max":self.length//2},#x
         "y":{"min":-self.max_height//2,"max":self.max_height//2},#y
         "z":{"min":-self.bredth//2,"max":self.bredth//2}#z
        }
        return limits
    
    def getRandomLoc(self,const_h=None):
        x=np.random.uniform(self.limits["x"]["min"],self.limits["x"]["max"])
        if const_h==None:
            y=np.random.uniform(self.limits["y"]["min"],self.limits["y"]["max"])
        else:
            y=np.clip(const_h,self.limits["y"]["min"],self.limits["y"]["max"])
        z=np.random.uniform(self.limits["z"]["min"],self.limits["z"]["max"])
        return Vec3(x,y,z)



if __name__=="__main__":
    app=Ursina()
    ground=Ground(100,100,50)
    EditorCamera()
    app.run()