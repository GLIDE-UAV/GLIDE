from ursina import Entity,color,destroy
try:from .constants import target_height
except:from constants import target_height
try:from .reward import target_destroy,nothing
except:from reward import target_destroy,nothing

class Target(Entity):
    def __init__(self,position,target_height=target_height):
        super().__init__()
        self.device="Target"
        self.target_height=target_height

        self.model="cube"
        self.collider="box"
        self.color=color.blue
        self.scale=(1,self.target_height,1)
        self.position=(position[0],position[1]+self.target_height/2,position[2])
        
        self.status="operational"
        self.enabled=True

    def reset(self,position):
        self.position=(position[0],position[1]+self.target_height/2,position[2])
        self.status="operational"
        self.enabled=True

    def update(self,type='distruction_radar'):
        if self.status=="operational":
            hitinfo=self.intersects()
            for ent in hitinfo.entities:
                if hasattr(ent,"device")==False:
                    continue
                elif ent.device==type:
                    self.destroy()
                    return target_destroy()
            return nothing()
        else:
            return target_destroy()

    def destroy(self):
        self.status="destroyed"
        self.enabled=False

    def deAllocate(self):
        destroy(self)
    
    def isDestroyed(self):
        return self.status=="destroyed"



if __name__=="__main__":
    from myursina import Ursina
    from ursina import EditorCamera
    app=Ursina()
    mine=Target(position=(0,0,0))
    EditorCamera()
    app.run()