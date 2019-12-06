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
        self.btnApplySettings.clicked.connect(self.updateSVG)
        """self.valOriginX.textChanged.connect(self.updateSVG)
        self.valOriginY.textChanged.connect(self.updateSVG)
        self.valOriginZ.textChanged.connect(self.updateSVG)
        self.valOriginRx.textChanged.connect(self.updateSVG)
        self.valOriginRy.textChanged.connect(self.updateSVG)
        self.valOriginRz.textChanged.connect(self.updateSVG)
        self.valPlunge.textChanged.connect(self.updateSVG)
        self.valMove.textChanged.connect(self.updateSVG)
        self.valScale.textChanged.connect(self.updateSVG)
        self.valTolerance.textChanged.connect(self.updateSVGtolerance)"""
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
        #options |= QFileDialog.DontUseNativeDialog
        self.fileName, _ = QFileDialog.getOpenFileName(self,"Openfile", "","SVG Files (*.svg);;All Files (*)", options=options)
        # self.processLoadFile.setValue(0)
        print(self.fileName)
        if self.fileName != "":
            self.valFileName.setText(self.fileName)
            self.svgblock.filepath = self.fileName
            self.svgblock.load()
            self.RB.loadSVG(self.svgblock,20)
        else:
            print("no file selected ")

    def Run(self):
        print("run")
        self.program.connectUR()
        self.program.run()
        pass

    def updateSVGtolerance(self):
        block = self.svgblock
        block.tolerance = self.update_text(self.valTolerance,10)
        self.svgblock.load()
        #self.RB.loadSVG(self.svgblock, 20)
        #self.RB.DrawCoords([0, 1, 1, 1], 10)
        #self.RB.paintGL()
        #self.RB.update()

    def updateSVG(self):
        print("updating svg settings")

        block = self.svgblock
        print(vars(self.svgblock))
        #block.coordinates_travel = self.valTravel
        block.travel_z = self.update_text(self.valMove)
        block.depth = self.update_text(self.valPlunge)
        # block.tolerance = float(self.valTolerance.text()) # this does not do anything, svg needs to be fulla reloaded
        block.scale = self.update_text(self.valScale,100) / 100

        new_origin = [self.update_text(self.valOriginX),
                  self.update_text(self.valOriginY),
                  self.update_text(self.valOriginZ),
                  self.update_text(self.valOriginRx, deg_to_rad=True),
                  self.update_text(self.valOriginRy, deg_to_rad=True),
                  self.update_text(self.valOriginRz, deg_to_rad=True)]
        block.csys = new_origin

        if block.tolerance != self.valTolerance.text():
            self.updateSVGtolerance()

        self.RB.loadSVG(self.svgblock, 20)
        #self.RB.DrawCoords([0,1,1,1],10)
        self.RB.paintGL()
        self.RB.update()

        print(vars(self.svgblock))

    def update_text(self,textfield,default=0,deg_to_rad=False):
        try:
            if deg_to_rad:
                value = DegToRad(float(textfield.text()))
            else:
                value = float(textfield.text())
        except:
            print("not a valid number value. value set to 0 instead")

            value = default
            textfield.setText(str(value))
        print(value)
        return value


class Program:

    def __init__(self):
        self.tcp = (0,0,0,0,pi,0)

        self.robot = None
        self.robotIP = "192.168.178.20"
        #self.connectUR()
        self.block_list = []
        self.units_in_meter = 1000  # urx uses meters this means all coordiante values will be divided by this to get the correct units



    def load_block(self, block):

        self.block_list.append(block)
        print("Blocklist:" + str(self.block_list))

        pass

    def run(self):

        print("running program")
        for block in self.block_list:
            self.runblockUR(block)

    def convert_path_units(self, path_to_conv):
        """All variables in this Program are in mm, however urx uses meters.
        This method converts between the two.
        it is called inside of self.runblockUR right before the robot commands are sent"""

        converted_path = path_to_conv

        for i, coord in enumerate(converted_path):
            print(coord)
            converted_path[i][0] = coord[0] / self.units_in_meter
            converted_path[i][1] = coord[1] / self.units_in_meter
            converted_path[i][2] = coord[2] / self.units_in_meter
            print(coord)
            print("--------")

        return converted_path

    def runblockUR(self, block):
        self.robot.set_tcp(self.tcp)
        print(self.tcp, "tcp set")

        csys = block.csys
        csys[0] /= self.units_in_meter
        csys[1] /= self.units_in_meter
        csys[2] /= self.units_in_meter
        print(csys)

        csys = m3d.Transform(csys)
        self.robot.set_csys(csys)
        print(csys)
        coords_to_send = block.coordinates_travel

        print(block.csys, "csys set")
        print("sending coordinates", coords_to_send)
        for i,path in enumerate(coords_to_send):
            print("converting path " + str(i) + "of " + str(len(coords_to_send)) )
            converted_p = self.convert_path_units(path)
            #print(path)
            #print(converted_p)
            print("___" * 40)
            self.robot.movexs(block.command, converted_p, block.a, block.v, block.radius)

    def connectUR(self):
        try:
            self.robot = urx.Robot(self.robotIP)
        except:
            print("retrying to connect to robot")
            time.sleep(1)
            self.connectUR()

        pose= self.robot.get_pose()
        print(pose)

        # self.robot.movej([0,-0.5*pi,-0.5*pi,-0.5*pi,0.5*pi,0],0.1,0.91)
        # time.sleep(20)

app = QApplication(sys.argv)
window = URPlayground()
window.setupUI()
window.show()
sys.exit(app.exec_())
#Program = Program()
#Block = svgBlock()
#Program.load_block(Block)
