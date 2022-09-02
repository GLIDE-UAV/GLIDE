try:from .radar import Radar
except:from radar import Radar
from ursina import Entity,color,destroy
try:from .constants import mine_radar_range
except:from constants import mine_radar_range
try:from .reward import mine_found,nothing
except:from reward import mine_found,nothing

class Advanced_Mine(Entity):
    def __init__(self,position,mine_radar_range=mine_radar_range,visible=False):
        super().__init__()
        self.device="Mine"

        self.model="sphere"
        self.collider='sphere'
        self.color=color.red
        self.scale=(1,1,1)
        self.position=position
        
        self.visible=visible
        self.status="hidden"
        self.enabled=True

        self.radar=Radar(self,mine_radar_range,color=color.rgba(217, 121, 228, 50),device="mine_radar")

    def reset(self,position,rader_radius):
        self.position=position
        self.radar.reset(rader_radius)
        self.visible=False
        self.status="hidden"
        self.enabled=True

    def update(self,type='detection_radar'):
        if self.status=="hidden":
            hitinfo=self.intersects()
            for ent in hitinfo.entities:
                if hasattr(ent,"device")==False:
                    continue
                elif ent.device==type:
                    self.visible=True
                    self.status="found"
                    return mine_found()
            return nothing()
        elif self.status=="found":
            return mine_found()
        else:
            return nothing()
        
    def destroy(self):
        self.status="destroyed"
        self.radar.destroy()
        self.enabled=False

    def deAllocate(self):
        destroy(self.radar)
        destroy(self)

    def isFound(self):
        return self.status=="found"

    def isDestroyed(self):
        self.status=="destroyed"


if __name__=="__main__":
    from myursina import Ursina
    from ursina import EditorCamera
    app=Ursina()
    amine=Advanced_Mine((10,0,0),10,True)
    EditorCamera()
    app.run()