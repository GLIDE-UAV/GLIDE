from ursina import *

class Target(Entity):
    def __init__(self,position,load_model=False,**kwargs):
        super().__init__()
        self.device="Target"
        self.parent=scene
        if load_model==True:
            self.model="Assets/target/target"
        else:
            self.model="sphere"
        self.scale=Vec3(1,4,1)
        self.position=position
        self.color=color.blue
        self.collider="box"
        self.status="operational"
        for key,value in kwargs.items():
            setattr(self,key,value)

    def update(self,type='distruction_radar'):
        if self.color==color.blue and self.status=="operational":
            hitinfo=self.intersects()
            for ent in hitinfo.entities:
                if ent.device==type:
                    self.destroy()
                    return 1 #target destroyed reward
        return 0

    def destroy(self):
        self.color=color.black50
        self.status="destroyed"
        self.enabled=False
    
    def isDestroyed(self):
        return self.status=="destroyed"



if __name__=="__main__":
    app=Ursina()
    mine=Target(position=(0,0,0))
    EditorCamera()
    app.run()