from math import pi

class Block():



    def __init__(self):

        self.csys = [0.6,0,0.3,0,pi,0]
        self.coordinates = []
        self.tcp = [0,0,0,0,0,0]
        self.a = 0.1
        self.v = 0.1
        self.radius = 0.01
        self.command = "movel"




    """def execute(self):
      robot.set_tcp(self.tcp)
      robot.set_csys(self.csys)
      robot.movexs(self.command,self.coordinates,self.radius,self.v,self.a)"""




