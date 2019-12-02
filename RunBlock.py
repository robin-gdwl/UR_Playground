from Main import Program

class RunUR(Program):

    def __init__(self):
        super(RunUR, self).__init__()

    def runblock(self,robot,block):

        robot.set_tcp(self.tcp)
        robot.set_csys(self.csys)
        robot.movexs(self.command, self.coordinates, self.radius, self.v, self.a)
