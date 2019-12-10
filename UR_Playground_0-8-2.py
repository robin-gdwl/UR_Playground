import sys
from Blocks import *
import time
from URPGwindow import Ui_MainWindow
import math3d as m3d
import urx
import logging
from SVG_Block import *
from PyQt5.QtWidgets import *
from PyQt5.uic import *
from Toolpath import Toolpath

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
logging.info("UR_PLAYGROUND_0.8.2")

class URPlayground(QMainWindow):

    def __init__(self, *args):
        self.starttime = time.time()
        super(URPlayground, self).__init__(*args)

        #loadUi("UR_playground_mainwindow03.ui",self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.objRB = Robot()
        self.RB = DrawRB.GLWidget(self, self.objRB)
        self.program = Program()
        self.svgblock = svgBlock()
        self.toolpath = None

        self.setWindowTitle("UR_Playground_0.8.2")

        self.initialise_blocks()
        #self.make_log()
        # TODO: this is bad, do it better with OOP:
        endtime = time.time()-self.starttime
        logging.info("Window loaded in " + str(endtime))

    def initialise_blocks(self):
        # TODO: make this parametric/ dynamic (1)
        logging.debug("initialising blocks: " + str(self.program.block_list))
        self.program.load_block(self.svgblock)

    def setupUI(self):
        logging.debug("setting up the UI")

        self.widgetP = self.ui.widgetPreview
        self.layoutP = QHBoxLayout(self)
        self.widgetP.setLayout(self.layoutP)
        self.layoutP.addWidget(self.RB)
        #self.hbox.addWidget(self.RB)

        #self.glwdgtPreview.
        self.ui.btnSelectFile.clicked.connect(self.openFileNameDialog)
        self.ui.btnSend.clicked.connect(self.Run)

        self.ui.btnApplyRobotSettings.clicked.connect(self.update_robot)
        self.ui.btnApplySVGSettings.clicked.connect(self.update_SVG)

        self.ui.btnCheck.clicked.connect(self.make_toolpath)
        #self.ui.btnPlay.clicked.connect(self.play_toolpath)
        self.ui.sliderPlay.valueChanged.connect(self.update_toolpath_position)

        self.ui.checkPlatform.stateChanged.connect(self.toggle_platform)
        self.ui.checkBoxes.stateChanged.connect(self.toggle_boxes)
        self.ui.checkGrid.stateChanged.connect(self.toggle_grid)
        # other signals form linetext: returnPressed,

        self.update_SVG()
        self.update_robot()
        self.make_log()

        endtime = time.time() - self.starttime
        logging.info("Window loaded in " + str(endtime))

    def check_toolpath(self):  # FIXME ... this is not done well at all fix this asap
        print("checking toolpath")
        toolpath = Toolpath(self.svgblock.coordinates_travel[0], self.program.tcp[2])
        coordinates = copy.copy(self.svgblock.coordinates_travel)
        previous_pose = self.objRB.q
        csys = m3d.Transform(self.svgblock.csys)
        tcp = m3d.Transform(self.program.tcp)
        print("tcp and csys:")
        print(tcp)
        print(csys)
        print("_____" * 25)
        for i, path in enumerate(coordinates):
            for coord in path:
                #convert coordinate to world coordinate system

                t = csys * m3d.Transform(coord)
                t = t * tcp

                #print("t" +str(t))

                pose = t.pose_vector
                #print("pose",pose)
                #self.RB.specialPoints = np.append(self.RB.specialPoints, [pose[:3]], axis=0)
                theta = pose[3:6]
                rot_mat = toolpath.eulerAnglesToRotationMatrix(theta)

                desired_pose = rot_mat
                p_column = np.array([[pose[0]/1000],[pose[1]/1000],[pose[2]/1000]])
                #print(p_column)

                full_matrix = np.append(rot_mat, p_column,axis=1)
                full_matrix = np.append(full_matrix, [[0,0,0,1]],axis = 0)
                #print(full_matrix)
                #print(coord)

                best_jpose = toolpath.invKine(full_matrix, previous_pose)
                #self.objRB.JVars = best_jpose[:,1]
                toolpath.poses.append(best_jpose)
                previous_pose = best_jpose

        self.toolpath = toolpath.poses
        print("tp ", self.toolpath)
            #return toolpath.poses
        del toolpath

        #self.objRB.JVars = best_jpose
        #self.RB.update()

    def play_toolpath(self):
        for i in range(100):
            if self.toolpath:

                tp_position = len(self.toolpath) * i / 100
                self.objRB.JVars = self.toolpath[int(tp_position)]
                self.RB.update()
                time.sleep(0.2)
            #else:
                #logging.info("No Toolpath. click check first")

    def make_toolpath(self):
        if len(self.svgblock.coordinates_travel) >0:
            self.toolpath = None
            self.check_toolpath()
            tp_position = len(self.toolpath) * self.ui.sliderPlay.sliderPosition()/100
            self.objRB.JVars = self.toolpath[int(tp_position)]
            self.RB.update()
        else:
            logging.info("No Toolpath. Load SVG File first")

    def update_toolpath_position(self):
        #print("slider position: ", self.ui.sliderPlay.sliderPosition())
        if self.toolpath:

            tp_position = len(self.toolpath) * self.ui.sliderPlay.sliderPosition() / 100
            self.objRB.JVars = self.toolpath[int(tp_position)]
            self.RB.update()
        else: logging.info("No Toolpath. click check first")

    def make_log(self):
        logTextBox = QTextEditLogger(self.ui.txtLog)
        # You can format what is printed to text box
        logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',"%H:%M:%S"))
        logging.getLogger().addHandler(logTextBox)
        # You can control the logging level
        logging.getLogger().setLevel(logging.INFO)

    def toggle_platform(self):
        self.RB.isDrawEnv = self.ui.checkPlatform.isChecked()
        self.RB.update()

    def toggle_boxes(self):
        self.RB.isDrawBox = self.ui.checkBoxes.isChecked()
        self.RB.update()

    def toggle_grid(self):
        self.RB.isDrawGrid = self.ui.checkGrid.isChecked()
        self.RB.update()

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
            self.ui.valFileName.setText(self.fileName)
            self.svgblock.filepath = self.fileName
            self.svgblock.load()
            self.update_SVG()
            self.RB.loadSVG(self.svgblock,20)
            self.RB.update()
        else:
            #print("no file selected ")
            logging.info("no file selected")


    def Run(self):
        #print("run")
        logging.info("running Program")
        self.update_SVG()
        self.update_robot()

        self.program.connectUR()
        time.sleep(1)
        if self.program.is_connected == True:
            self.program.run()
            self.program.disconnectUR()
        else:
            #logging.info("No Robot connected try again")
            pass

    def updateSVGtolerance(self):
        block = self.svgblock
        block.tolerance = self.update_text(self.ui.valTolerance,10)
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
        block.travel_z = self.update_text(self.ui.valMove)
        block.depth = self.update_text(self.ui.valPlunge)
        # block.tolerance = float(self.valTolerance.text()) # this does not do anything, svg needs to be fulla reloaded
        block.scale = self.update_text(self.ui.valScale,100) / 100
        block.radius = self.update_text(self.ui.valBlend)

        block.use_colour = self.ui.checkUseColor.isChecked()
        block.use_opacity = self.ui.checkUseOpacity.isChecked()
        block.color_effect = self.update_text(self.ui.valColorFactor, 100) / 100
        block.opacity_effect = self.update_text(self.ui.valOpacityFactor, 100) / 100

        new_origin = [self.update_text(self.ui.valOriginX),
                  self.update_text(self.ui.valOriginY),
                  self.update_text(self.ui.valOriginZ),
                  self.update_text(self.ui.valOriginRx, deg_to_rad=True),
                  self.update_text(self.ui.valOriginRy, deg_to_rad=True),
                  self.update_text(self.ui.valOriginRz, deg_to_rad=True)]
        block.csys = new_origin

        try:
            if block.tolerance != self.ui.valTolerance.text():
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
            #textfield.setText(str(value))
        except:
            value = default
            textfield.setText(str(value))
            logging.info("Not a valid number in" + str(textfield) + " value set to " + str(default) + " instead")

        logging.debug("value set: " + str(value))
        return value

    def update_robot(self):
        logging.info("Applying Robot Settings")

        block = self.svgblock
        self.program.robotIP = self.ui.valRobotIP.text()  # does not use the self.update_text method as it is not a number
        self.program.tcp[2] = self.update_text(self.ui.valToolLength)
        self.RB.toollength = self.update_text(self.ui.valToolLength)
        block.v = self.update_text(self.ui.valSpeed) / 100
        block.a = self.update_text(self.ui.valAccell) /100

        self.RB.update()

class QTextEditLogger(logging.Handler):
    def __init__(self, textwidget):
        super().__init__()
        self.widget = textwidget
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)

class Program:

    def __init__(self):
        self.tcp = [0,0,0,0,pi,0] # FIXME: this is a workaround, the direciton change should happen elsewhere

        self.robot = None
        self.is_connected = False
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
            robot_accel = a * 1
            robot_speed = v * 1

        return robot_accel, robot_speed


    def runblockUR(self, block):

        conv_tcp = self.convert_tcp_units()
        self.robot.set_tcp(conv_tcp)
        logging.debug("TCP set: " +str(conv_tcp))

        csys = copy.copy(block.csys) # TODO: figure out if this is the right way to do this- I have not yet understood how data should be handled here
        csys[0] /= self.units_in_meter
        csys[1] /= self.units_in_meter
        csys[2] /= self.units_in_meter
        #print(csys)

        csys = m3d.Transform(csys)
        self.robot.set_csys(csys)
        logging.debug("CSYS set: " + str(csys))

        coords_to_send = copy.copy(block.coordinates_travel) # FIXME: why does this not work? the second time the block is executed

        acceleration, velocity = self.convert_v_a(block.a, block.v)

        logging.info("TCP set: " +str(conv_tcp)+ "CSYS set: " + str(csys))

        #print(block.csys, "csys set")
        #print("sending coordinates", coords_to_send)

        for i,path in enumerate(coords_to_send):
            #print("converting path " + str(i) + "of " + str(len(coords_to_send)) )
            logging.debug("converting path " + str(i) + "of " + str(len(coords_to_send)))
            converted_p = self.convert_path_units(path)
            logging.debug(block.command + str(acceleration) + str(velocity))
            #print(path)
            print(converted_p)
            print("___" * 40)
            try:
                logging.info("Sending move commands. First coordinate:  " + str(converted_p[0]))
                time.sleep(0.01)
                self.robot.movexs(block.command, converted_p, acceleration, velocity, block.radius / self.units_in_meter)
                print("executing path")
            except:
                print("something went wrong at robot")
                logging.info("Something went wrong while sending commands to the robot")
                break

    def connectUR(self, tries=1):
        max_tries = 3
        logging.info("Connecting to UR-Robot")
        try:
            self.robot = urx.Robot(self.robotIP)
            logging.debug("successfully connected to robot")
            self.is_connected = True
        except:
            #print("retrying to connect to robot")
            logging.info(" Robot connection failed, retrying to connect to robot. Tries: " + str(tries))
            time.sleep(3)
            if tries < max_tries:
                tries += 1
                self.connectUR(tries)
            else:
                logging.info("failed to connect after " +str(max_tries)+" tries. Please check your connection")

        try:
            pose= self.robot.get_pose()
        except:
            pass
        #print(pose)

    def disconnectUR(self):
        try:
            self.is_connected = False
            self.robot.close()
        except:
            pass

def main():
    """main function that is executed on startup """
    app = QApplication(sys.argv)
    window = URPlayground()
    window.setupUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()  # runs main function, creates UI etc.