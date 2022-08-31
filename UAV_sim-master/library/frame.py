from ursina import *

class Frame(Entity):
    def __init__(self,length,bredth,max_height,**kwargs):
        super().__init__()
        self.length=length
        self.bredth=bredth
        self.max_height=max_height

        self.parent=scene
        self.model="wireframe_cube"
        self.scale=Vec3(length,max_height,bredth)
        self.position=Vec3(0,0,0)
        self.limits=self.getLimits()
        self.color=color.white50
        for key,value in kwargs.items():
            setattr(self,key,value)

    def getLimits(self):
        limits={
         "x":{"min":-self.length//2,"max":self.length//2},#x
         "y":{"min":-self.max_height//2,"max":self.max_height//2},#y
         "z":{"min":-self.bredth//2,"max":self.bredth//2}#z
        }
        return limits

    def isOutSide(self,obj):
        for i,dir in enumerate(["x","y","z"]):
            if (self.limits[dir]["min"]<=obj.position[i]<=self.limits[dir]["max"])==False:
                return True
        return False



if __name__=="__main__":
    app=Ursina()
    camera.set_position(Vec3(0, 0, -230.337))
    frame=Frame(100,100,50)
    EditorCamera()
    app.run()