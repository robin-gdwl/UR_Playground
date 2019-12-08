import sys
from Blocks import *
import time
import math3d as m3d
import urx
import logging
from SVG_Block import *
from PyQt5.QtWidgets import *
from PyQt5.uic import *

import OpenGLControl as DrawRB
from Robot import *
from Trajectory import *

class BlockViewer():
    """
    NOT USED ATM
    gets a BLOCK object and uses its csys to place all points in space
    these points will later be displayed in the opengl window"""
    pass

logging.basicConfig(filename= "UR_Playground.log", level=logging.DEBUG,
                    format = "%(asctime)s:%(levelname)s:%(message)s")
logging.info("___"*45)
logging.info("UR_PLAYGROUND")

class URPlayground(QMainWindow):

    def __init__(self, *args):
        starttime = time.time()
        super(URPlayground, self).__init__(*args)

        loadUi("UR_playground_mainwindow03.ui",self)
        self.objRB = Robot()
        self.RB = DrawRB.GLWidget(self, self.objRB)
        self.program = Program()
        self.svgblock = svgBlock()

        self.initialise_blocks()
        # TODO: this is bad, do it better with OOP:
        endtime = time.time()-starttime
        logging.info("Window loaded in " + str(endtime))

    def initialise_blocks(self):
        # TODO: make this parametric/ dynamic (1)
        logging.debug("initialising blocks: " + str(self.program.block_list))
        self.program.load_block(self.svgblock)

    def setupUI(self):
        logging.debug("setting up the UI")

        self.widgetP = self.widgetPreview
        self.layoutP = QHBoxLayout(self)
        self.widgetP.setLayout(self.layoutP)
        self.layoutP.addWidget(self.RB)
        #self.hbox.addWidget(self.RB)

        #self.glwdgtPreview.
        self.btnSelectFile.clicked.connect(self.openFileNameDialog)
        self.btnSend.clicked.connect(self.Run)

        self.btnApplyRobotSettings.clicked.connect(self.update_robot)
        self.btnApplySVGSettings.clicked.connect(self.update_SVG)

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
        #print(self.fileName)
        logging.debug("file to be loaded: " + str(self.fileName))

        if self.fileName != "":
            self.valFileName.setText(self.fileName)
            self.svgblock.filepath = self.fileName
            self.svgblock.load()
            self.RB.loadSVG(self.svgblock,20)
            self.RB.update()
        else:
            #print("no file selected ")
            logging.info("no file selected")


    def Run(self):
        #print("run")
        logging.info("running Program")

        self.program.connectUR()
        time.sleep(2)
        self.program.run()
        self.program.disconnectUR()
        pass

    def updateSVGtolerance(self):
        block = self.svgblock
        block.tolerance = self.update_text(self.valTolerance,10)
        self.svgblock.load()
        #self.RB.loadSVG(self.svgblock, 20)
        #self.RB.DrawCoords([0, 1, 1, 1], 10)
        #self.RB.paintGL()
        #self.RB.update()

    def update_SVG(self):
        #print("updating svg settings")
        logging.info("Applying SVG Settings")
        # TODO: make this so only changed values are actually changed

        block = self.svgblock
        print(vars(self.svgblock))
        #block.coordinates_travel = self.valTravel
        block.travel_z = self.update_text(self.valMove)
        block.depth = self.update_text(self.valPlunge)
        # block.tolerance = float(self.valTolerance.text()) # this does not do anything, svg needs to be fulla reloaded
        block.scale = self.update_text(self.valScale,100) / 100
        block.radius = self.update_text(self.valBlend)

        block.use_colour = self.checkUseColor.isChecked()
        block.use_opacity = self.checkUseOpacity.isChecked()
        block.color_effect = self.update_text(self.valColorFactor, 100) / 100
        block.opacity_effect = self.update_text(self.valOpacityFactor, 100) / 100

        new_origin = [self.update_text(self.valOriginX),
                  self.update_text(self.valOriginY),
                  self.update_text(self.valOriginZ),
                  self.update_text(self.valOriginRx, deg_to_rad=True),
                  self.update_text(self.valOriginRy, deg_to_rad=True),
                  self.update_text(self.valOriginRz, deg_to_rad=True)]
        block.csys = new_origin

        try:
            if block.tolerance != self.valTolerance.text():
                self.updateSVGtolerance()

            self.RB.loadSVG(self.svgblock, 20)
            self.RB.paintGL()
            self.RB.update()
        except:
            logging.warning("No file loaded (?) unable to apply SVG settings")

        logging.debug(" finished applying SVG settings ----------------------------------")
        #print(vars(self.svgblock))

    def update_text(self,textfield,default=0,deg_to_rad=False):
        logging.debug("Setting values from " + str(textfield.objectName()) + ": " + str(textfield.text()))
        try:
            if deg_to_rad:
                value = DegToRad(float(textfield.text()))
                logging.debug("Target value is in radians")
            else:
                value = float(textfield.text())
            textfield.setText(str(value))
        except:
            value = default
            textfield.setText(str(value))
            logging.info("Not a valid number in" + str(textfield) + " value set to " + str(default) + " instead")

        logging.debug("value set: " + str(value))
        return value

    def update_robot(self):
        logging.info("Applying Robot Settings")

        block = self.svgblock
        self.program.robotIP = self.valRobotIP.text()  # does not use the self.update_text method as it is not a number
        self.program.tcp[2] = self.update_text(self.valToolLength)
        self.RB.toollength = self.update_text(self.valToolLength)
        block.v = self.update_text(self.valSpeed) / 100
        block.a = self.update_text(self.valAccell) /100

        self.RB.update()


class Program:

    def __init__(self):
        self.tcp = [0,0,0,0,pi,0] # FIXME: this is a workaround, the direciton change should happen elsewhere

        self.robot = None
        self.robotIP = "192.168.178.20"
        #self.connectUR()
        self.block_list = []
        self.units_in_meter = 1000  # urx uses meters this means all coordiante values will be divided by this to get the correct units
        logging.debug("Program class initiated")

    def load_block(self, block):

        self.block_list.append(block)
        #print("Blocklist:" + str(self.block_list))
        logging.debug("Blocklist:" + str(self.block_list))

    def run(self):

        #print("running program")
        for block in self.block_list:
            self.runblockUR(block)

    def convert_tcp_units(self):
        converted_tcp = copy.copy(self.tcp)
        converted_tcp[0] /= self.units_in_meter
        converted_tcp[1] /= self.units_in_meter
        converted_tcp[2] /= self.units_in_meter
        return converted_tcp

    def convert_path_units(self, path_to_conv):
        """All variables in this Program are in mm, however urx uses meters.
        This method converts between the two.
        it is called inside of self.runblockUR right before the robot commands are sent"""

        converted_path = copy.copy(path_to_conv) # TODO: figure out if this is the right way to do this- I have not yet understood how data should be handled here

        for i, coord in enumerate(converted_path):
            converted_path[i][0] = coord[0] / self.units_in_meter
            converted_path[i][1] = coord[1] / self.units_in_meter
            converted_path[i][2] = coord[2] / self.units_in_meter

        return converted_path

    def convert_v_a(self, a, v, jointspeed = False):
        """the values for velocity(speed) and accelleration are set in percent in the UI
        this method multiplies the percentage with the maximum speed and acceleration values of the robot """
        # TODO: the maximum speed and acceleration for a robot should be set in the ConfigRobot File not here

        if jointspeed:
            robot_accel = a * 0.349
            robot_speed = v * 0.524

        else:
            robot_accel = a * 0.1
            robot_speed = v * 0.1

        return robot_accel, robot_speed


    def runblockUR(self, block):

        conv_tcp = self.convert_tcp_units()
        self.robot.set_tcp(conv_tcp)
        logging.debug("TCP set: " +str(conv_tcp))

        csys = copy.copy(block.csys) # TODO: figure out if this is the right way to do this- I have not yet understood how data should be handled here
        csys[0] /= self.units_in_meter
        csys[1] /= self.units_in_meter
        csys[2] /= self.units_in_meter
        print(csys)

        csys = m3d.Transform(csys)
        self.robot.set_csys(csys)
        logging.debug("CSYS set: " + str(csys))
        coords_to_send = block.coordinates_travel

        acceleration, velocity = self.convert_v_a(block.a, block.v)

        #print(block.csys, "csys set")
        #print("sending coordinates", coords_to_send)

        for i,path in enumerate(coords_to_send):
            #print("converting path " + str(i) + "of " + str(len(coords_to_send)) )
            logging.debug("converting path " + str(i) + "of " + str(len(coords_to_send)))
            converted_p = self.convert_path_units(path)
            logging.debug(block.command + str(acceleration) + str(velocity))
            #print(path)
            #print(converted_p)
            #print("___" * 40)
            self.robot.movexs(block.command, converted_p, acceleration, velocity, block.radius)

    def connectUR(self, tries=0):
        logging.info("Connecting to UR-Robot")
        try:
            self.robot = urx.Robot(self.robotIP)
        except:
            #print("retrying to connect to robot")
            logging.info(" Robot connection failed, retrying to connect to robot. Tries: " + str(tries))
            #time.sleep(0)
            tries += 1
            self.connectUR(tries)

        pose= self.robot.get_pose()
        #print(pose)

    def disconnectUR(self):
        self.robot.close()

def main():
    """main function that is executed on startup """
    app = QApplication(sys.argv)
    window = URPlayground()
    window.setupUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()  # runs main function, creates UI etc.