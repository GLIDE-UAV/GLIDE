from ursina import *
try:from .radar import Radar
except:from radar import Radar
try:from .constants import mine_radar_range
except:from constants import mine_radar_range

class Advanced_Mine(Entity):
    def __init__(self,position,mine_radar_range=mine_radar_range,visible=False,**kwargs):
        super().__init__()
        self.device="Mine"
        self.parent=scene
        self.model="sphere"
        self.collider='sphere'
        self.scale=Vec3(1,1,1)
        self.position=position
        self.color=color.red
        self.visible=visible
        self.status="hidden"
        self.rader=Radar(self,mine_radar_range,color=color.rgba(217, 121, 228, 30),device="mine_radar")
        for key,value in kwargs.items():
            setattr(self,key,value)

    def update(self,type='detection_radar'):
        if self.visible==False and self.status=="hidden":
            hitinfo=self.intersects()
            for ent in hitinfo.entities:
                if ent.device==type:
                    self.visible=True
                    self.status="found"
                    return 1 #detection reward
        return 0
        
    def destroy(self):
        self.color=color.black50
        self.status="destroyed"
        self.enabled=False

    def isFound(self):
        return self.status=="found"

    def isDestroyed(self):
        self.status=="destroyed"


if __name__=="__main__":
    app=Ursina()
    amine=Advanced_Mine((10,0,0),10,True)
    EditorCamera()
    app.run()