from ursina import Entity,color,destroy
    
class Radar(Entity):
    def __init__(self,parent,radius,color=color.black,device="radar"):
        super().__init__()
        self.device=device
        self.parent=parent

        self.model="sphere"
        self.collider="sphere"
        self.color=color
        self.scale=2*radius
        self.enabled=True

    def reset(self,radius):
        self.scale=2*radius
        self.enabled=True

    def destroy(self):
        self.scale=(0,0,0)
        self.enabled=False

    def deAllocate(self):
        destroy(self)


if __name__=="__main__":
    from myursina import Ursina
    from ursina import EditorCamera
    app=Ursina()
    ent=Entity(position=(0,0,0),model="cube",scale=1)
    rader=Radar(ent,10,color.black33,"distruction_radar")
    rader2=Radar(ent,20,color.black10,"detection_radar")
    EditorCamera()
    app.run()