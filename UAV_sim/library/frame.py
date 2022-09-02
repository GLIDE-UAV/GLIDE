from ursina import Entity,color

class Frame(Entity):
    def __init__(self,length,bredth,max_height):
        super().__init__()
        self.length=length
        self.bredth=bredth
        self.max_height=max_height

        self.model="wireframe_cube"
        self.color=color.white50
        self.scale=(length,max_height,bredth)
        self.position=(0,0,0)
        self.limits=self.getLimits()

    def getLimits(self):
        limits={
         "x":{"min":-self.length//2,"max":+self.length//2},
         "y":{"min":-self.max_height//2,"max":+self.max_height//2},
         "z":{"min":-self.bredth//2,"max":+self.bredth//2}
        }
        return limits

    def isOutSide(self,obj):
        for dir in ["x","y","z"]:
            if (self.limits[dir]["min"]<=getattr(obj,dir)<=self.limits[dir]["max"])==False:
                return True
        return False



if __name__=="__main__":
    from myursina import Ursina
    from ursina import camera,EditorCamera
    app=Ursina()
    camera.set_position((0, 0, -230.337))
    frame=Frame(100,100,50)
    EditorCamera()
    app.run()