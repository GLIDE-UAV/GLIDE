from ursina import *
    
class Radar(Entity):
    def __init__(self,parent,radius,color=color.black,device="radar"):
        super().__init__()
        self.device=device
        self.parent=parent
        self.model="sphere"
        self.scale=2*radius #2 time scaling is required
        self.collider="sphere"
        self.color=color

    def destroy(self):
        self.parent.destroy()
        destroy(self)


if __name__=="__main__":
    app=Ursina()
    ent=Entity(position=(0,0,0),model="cube",scale=1)
    rader=Radar(ent,10,color.black33,"distruction_radar") #r1 m
    rader2=Radar(ent,20,color.black10,"detection_radar") #r2 m
    EditorCamera()
    app.run()