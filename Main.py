import sys

from Blocks import *
#from RunBlock import Run
from SVG_Block import *
import time
import math3d as m3d
from math import pi
import urx

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.uic import *
import OpenGLControl as DrawRB

import OpenGLControl as DrawRB
from Robot import *
from Trajectory import *

class BlockViewer():
    """gets a BLOCK object and uses its csys to place all points in space
    these points will later be displayed in the opengl window"""

    pass

class URPlayground(QMainWindow):

    def __init__(self, *args):
        super(URPlayground, self).__init__(*args)

        loadUi("UR_playground_mainwindow03.ui",self)
        self.objRB = Robot()
        self.RB = DrawRB.GLWidget(self, self.objRB)
        self.program = Program()
        self.svgblock = svgBlock()
        #self.UpdateData(1)
        #self.UpdateData(2)

        self.initialise_blocks()
        # TODO: this is bad, do it better with OOP:

    def initialise_blocks(self):
        # TODO: make this parametric/ dynamic (1)
        self.program.load_block(self.svgblock)

    def setupUI(self):
        #self.setCentralWidget(self.RB)
        #preview = self.RB

        self.widgetP = self.widgetPreview
        self.layoutP = QHBoxLayout(self)
        self.widgetP.setLayout(self.layoutP)
        self.layoutP.addWidget(self.RB)
        #self.hbox.addWidget(self.RB)

        #self.glwdgtPreview.
        self.btnSelectFile.clicked.connect(self.openFileNameDialog)

        self.btnSend.clicked.connect(self.Run)

        print(type(svgBlock))
        self.valOriginX.textChanged.connect(self.updateSVG)
        self.valOriginY.textChanged.connect(self.updateSVG)
        self.valOriginZ.textChanged.connect(self.updateSVG)
        self.valOriginRx.textChanged.connect(self.updateSVG)
        self.valOriginRy.textChanged.connect(self.updateSVG)
        self.valOriginRz.textChanged.connect(self.updateSVG)
        self.valPlunge.textChanged.connect(self.updateSVG)
        self.valMove.textChanged.connect(self.updateSVG)
        self.valScale.textChanged.connect(self.updateSVG)
        self.valTolerance.textChanged.connect(self.updateSVG)
        # other signals form linetext: returnPressed,

    def ShowAbout(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("UR Playground")
        msg.setInformativeText("UR_Playground is a software tool to facilitate explorative and artistic work with universal robots. Developed at BURG Giebichenstein University of ARt and Design Halle, Germany. \
            \n\nCode by: Robin Godwyll building on top of \"Robot Simulator\" by Nguyen Van Khuong\
            \nSource code: https://github.com/boundlessmaking/UR_Playground\
            \nVideo demo: https://tinyurl.com/robot-simulation-python-opengl")
        msg.setWindowTitle("About UR_Playground")
        msg.exec_()


    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.fileName, _ = QFileDialog.getOpenFileName(self,"Openfile", "","SVG Files (*.svg);;All Files (*)", options=options)
        # self.processLoadFile.setValue(0)
        self.valFileName.setText(self.fileName)
        self.svgblock.filepath = self.fileName
        self.svgblock.load()
        self.RB.loadSVG(self.svgblock,20)
        #self.valueStatus.setText("None...")

    """def LoadFile(self):
        #self.UpdateData(1)
        #self.UpdateData(2)
        if self.fileName == None:
            self.valueStatus.setText("Error: file is not found")
        else:
            self.count = 0
            self.RB.listPoints = np.array([[0,0,0]])
            self.RB.color=np.array([0])
            self.AllPoints = np.array([[None, None, None]])
            self.AllJVars = np.array([[None, None, None, None]])
            self.toolstatus = np.array([None])

            #self.valueStatus.setText("Processing...")
            # self.processLoadFile.setValue(30)
            listPoint = LoadGCode(self.fileName, self.objRB.EVars[0], self.objRB.EVars[1], self.objRB.EVars[2])
            self.update()
            trj = Trajectory()
            listPoint = np.insert(listPoint, 0, [self.objRB.EVars[0], self.objRB.EVars[1], self.objRB.EVars[2], 0], axis = 0)
            listPoint = np.append(listPoint, [[self.objRB.EVars[0], self.objRB.EVars[1], self.objRB.EVars[2], 0]], axis = 0)
            toolstt_tmp = np.array([None])
            trj.SetSpTime(0.1)
            for i in np.arange(len(listPoint)-1):
                p1 = listPoint[i][:3]
                p2 = listPoint[i+1][:3]
                if i==0 or i == len(listPoint)-2:
                    trj.SetPoint(p1,p2,100)
                else:
                    trj.SetPoint(p1, p2, 100)
                points = trj.Calculate()
                if points[0] == False:
                    pass
                else:
                    self.AllPoints = np.append(self.AllPoints, points[1], axis = 0)
                    self.toolstatus = np.append(self.toolstatus, [listPoint[i+1][3]]*len(points[1]))

            self.toolstatus = np.delete(self.toolstatus, 0)
            self.AllPoints = np.delete(self.AllPoints, 0, axis = 0)
            toolstt_tmp = np.delete(toolstt_tmp, 0)
            q1P = self.objRB.q1P
            q2P = self.objRB.q2P
            for p in self.AllPoints:
                EVars = np.append(p, [self.objRB.EVars[3], self.objRB.EVars[4], self.objRB.EVars[5]])
                JVar = self.objRB.CalInvPositionEx(EVars, q1P, q2P)
                if JVar[0] == False:
                    break
                self.AllJVars = np.append(self.AllJVars, [JVar[1]], axis = 0)
                q2P = q1P
                q1P = JVar[1]

            self.AllJVars = np.delete(self.AllJVars, 0, axis = 0)
            # self.processLoadFile.setValue(100)

            if len(self.AllJVars) == len(self.AllPoints):
                self.valueStatus.setText("All done")
            else:
                self.valueStatus.setText("Some points is missing")
"""

    """def LoadFile(self):
        self.svgblock.load()"""


    def Run(self):

        print("run")
        pass

    def updateSVG(self):
        print("updating svg settings")


        block = self.svgblock
        print(vars(self.svgblock))
        #block.coordinates_travel = self.valTravel
        block.travel_z = float(self.valMove.text())
        block.depth = float(self.valPlunge.text())
        block.tolerance = float(self.valTolerance.text())
        block.scale = float(self.valScale.text())

        origin = [float(self.valOriginX.text()),
                  float(self.valOriginY.text()),
                  float(self.valOriginZ.text()),
                  float(self.valOriginRx.text()),
                  float(self.valOriginRy.text()),
                  float(self.valOriginRz.text())]
        block.csys = origin

        self.RB.loadSVG(self.svgblock, 20)
        self.RB.DrawCoords([0,1,1,1],10)

        print(vars(self.svgblock))


class Program:

    def __init__(self):
        self.tcp = (0,0,0,0,0,0)

        self.robot = None
        self.robotIP = "192.168.178.20"
        #self.connectUR()
        self.block_list = []



    def load_block(self, block):

        self.block_list.append(block)
        print("Blocklist:" + str(self.block_list))

        pass

    def run(self):

        for block in self.block_list:
            self.runblockUR(block)

    def runblockUR(self, block):
        self.robot.set_tcp(self.tcp)
        print(self.tcp, "tcp set")

        csys = m3d.Transform(block.csys)
        self.robot.set_csys(csys)

        print(block.csys, "csys set")
        print("sending coordinates", block.coordinates_travel)
        for path in block.coordinates_travel:
            self.robot.movexs(block.command, path, block.a, block.v, block.radius)

    def connectUR(self):
        try:
            self.robot = urx.Robot(self.robotIP)
        except:
            print("retrying to connect to robot")
            time.sleep(1)
            self.connectUR()

        pose= self.robot.get_pose()
        print(pose)

        #self.robot.movej([0,-0.5*pi,-0.5*pi,-0.5*pi,0.5*pi,0],0.1,0.91)
        #time.sleep(20)

app = QApplication(sys.argv)
window = URPlayground()
window.setupUI()
window.show()
sys.exit(app.exec_())
#Program = Program()
#Block = svgBlock()
#Program.load_block(Block)

"""

testblock = svgBlock()
testblock.filepath = "Test03.svg"
paths = testblock.load()

TESTPROG = Program()
TESTPROG.load_block(testblock)
TESTPROG.run()"""