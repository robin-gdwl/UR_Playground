from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import pyqtSignal, QPoint, QSize, Qt
from PyQt5.QtGui import QColor, QOpenGLVersionProfile
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QOpenGLWidget, QSlider,
        QWidget)
from PyQt5 import QtOpenGL
from OpenGL import GLU
from OpenGL.GL import *
from OpenGL.GLUT import *
from numpy import array, arange
import numpy as np
import math3d as m3d
from STLFile import Loader
# from ConfigRobot import *
from GlobalFunc import *


class GLWidget(QOpenGLWidget):
    xRotationChanged = QtCore.pyqtSignal(int)
    yRotationChanged = QtCore.pyqtSignal(int)
    zRotationChanged = QtCore.pyqtSignal(int)

    def __init__(self, parent=None, objRobot=None):
        super(GLWidget, self).__init__(parent)
        self.objRobot = objRobot
        self.xRot = -2584
        self.yRot = 1376
        self.zRot = 0.0
        self.z_zoom = -3000
        self.xTran = 0
        self.yTran = 0
        self.isDrawGrid = False;
        self.isDrawEnv = True
        self.isDrawBox = True
        #print("Loading stl files...")
        #self.fullrobot = Loader("3DFiles/UR_lowres01_05.stl")
        self.model0 = Loader('UR5-0.STL')
        self.model1 = Loader('UR5-1.STL')
        self.model2 = Loader('UR5-2.STL')
        self.model3 = Loader('UR5-3.STL')
        self.model4 = Loader('UR5-4.STL')
        self.model5 = Loader('UR5-5.STL')
        self.model6 = Loader('UR5-6.STL')
        self.modelplatform = Loader('env_platform01.stl')
        self.modelboxes = Loader('env_boxes01.stl')
        self.toollength = 0  # TODO: could this be done differently, without this extra property?
        #print("All done.")

        self.listPoints = np.array([[0,0,0]]) # not used atm will be used in the future
        self.listCoords = np.array([[0,0,0]])
        self.specialPoints = np.array([[0,0,0]])  # draws file origins in the preview

        self.AllList = np.array([self.listPoints])
        self.stt = np.array([])
        self.color=np.array([0])

    def setXRotation(self, angle):
        self.normalizeAngle(angle)
        if angle != self.xRot:
            self.xRot = angle
            self.xRotationChanged.emit(angle)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            self.update()

    def setYRotation(self, angle):
        self.normalizeAngle(angle)
        if angle != self.yRot:
            self.yRot = angle
            self.yRotationChanged.emit(angle)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            # self.update(

    def setZRotation(self, angle):
        self.normalizeAngle(angle)
        if angle != self.zRot:
            self.zRot = angle
            self.zRotationChanged.emit(angle)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            self.update()

    def setXYTranslate(self, dx, dy):
        self.xTran += 3.0 * dx
        self.yTran -= 3.0 * dy
        self.update()

    def setZoom(self, zoom):
        #print("zooming")
        self.z_zoom = zoom
        self.update()

    def updateJoint(self):
        #print("updating joint")
        self.update()

    def initializeGL(self):
        #print("initialising GL")
        lightPos = (5.0, 5.0, 10.0, 1.0)
        reflectance1 = (0.8, 0.1, 0.0, 1.0)
        reflectance2 = (0.0, 0.8, 0.2, 1.0)
        reflectance3 = (0.2, 0.2, 1.0, 1.0)

        ambientLight = [0.7, 0.7, 0.7, 1.0]
        diffuseLight = [0.7, 0.8, 0.8, 1.0]
        specularLight = [0.4, 0.4, 0.4, 1.0]
        positionLight = [20, 20, -30, 0.0]

        glLightfv(GL_LIGHT0, GL_AMBIENT, ambientLight);
        glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuseLight)
        glLightfv(GL_LIGHT0, GL_SPECULAR, specularLight)
        glLightModelf(GL_LIGHT_MODEL_TWO_SIDE, 1.0)
        glLightfv(GL_LIGHT0, GL_POSITION, positionLight)
        #initializeOpenGLFunctions()

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_NORMALIZE)
        # glEnable(GL_BLEND);
        glClearColor(1, 1, 1, 1.0)

    def draw_tool(self):
        """draws a line with a point at the end representing the tool attached to the robot
        The length of the tool can be set in the Robot settings in the UI """

        self.setupColor([25 / 255, 99 / 255.0, 94 / 255])
        glLineWidth(6)
        glBegin(GL_LINES);
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, self.toollength)
        glEnd()
        glPointSize(15);
        glBegin(GL_POINTS)
        glVertex3f(0,0, self.toollength)
        glEnd()
        pass


    def draw_robot(self):
        glPushMatrix()

        self.setupColor([1 / 255, 141 / 255.0, 133 / 255])
        glRotatef(180, 0, 0, 1);
        self.model0.draw()
        # self.setupColor([169.0 / 255, 169.0 / 255, 169.0 / 255])

        # Link1
        self.setupColor([25 / 255, 99 / 255.0, 94 / 255])
        glTranslatef(0.0, 0.0, self.objRobot.d[1]);
        glRotatef(RadToDeg(self.objRobot.JVars[0]), 0.0, 0.0, 1.0)
        glTranslatef(self.objRobot.a[1], 0.0, 0.0)
        glRotatef(RadToDeg(self.objRobot.alpha[0]), 0, 0, 1);
        self.model1.draw()

        # Link2
        self.setupColor([1 / 255, 142 / 255.0, 133 / 255])
        glTranslatef(0.0, 135.85, 0);
        glRotatef(RadToDeg(self.objRobot.JVars[1]), 0.0, 1, 0)
        # glTranslatef(0, 0.0,self.objRobot.a[2])
        glRotatef(RadToDeg(self.objRobot.alpha[1]), 0, 1, 0.0);
        self.model2.draw()

        # Link3
        self.setupColor([25 / 255, 99 / 255.0, 94 / 255])
        glTranslatef(0.0, -119.7, 425);
        glRotatef(RadToDeg(self.objRobot.JVars[2]), 0.0, 1, 0)
        # glTranslatef(self.objRobot.a[3], 0.0, 0.0)
        glRotatef(RadToDeg(self.objRobot.alpha[2]), 0, 1, 0.0);
        self.model3.draw()

        # Link4
        self.setupColor([1 / 255, 142 / 255.0, 133 / 255])
        glTranslatef(0.0, 0.0, 392.25);
        glRotatef(RadToDeg(self.objRobot.JVars[3]), 0.0, 1, 0)
        # glTranslatef(self.objRobot.a[4], 0.0, 0.0)
        glRotatef(RadToDeg(self.objRobot.alpha[3]), 0, 1, 0.0);
        self.model4.draw()
        self.setupColor([0.0 / 255, 180.0 / 255, 84.0 / 255])

        # Link5
        self.setupColor([25 / 255, 99 / 255.0, 94 / 255])
        glTranslatef(0, 93, 0);
        glRotatef(RadToDeg(self.objRobot.JVars[4]), 0.0, 0.0, 1.0)
        # glTranslatef(self.objRobot.a[5], 0.0, 0.0)
        glRotatef(RadToDeg(self.objRobot.alpha[4]), 0, 0, 1);
        self.model5.draw()

        # Link6
        self.setupColor([1 / 255, 142 / 255.0, 133 / 255])
        glTranslatef(0, 0, 94.65);
        glRotatef(RadToDeg(self.objRobot.JVars[5]), 0.0, 1, 0)
        # glTranslatef(self.objRobot.a[5], 0.0, 0.0)
        glRotatef(RadToDeg(self.objRobot.alpha[5]), 1.0, 0.0, 0.0);
        self.model6.draw()

        glTranslate(0, self.objRobot.d[5], 0)
        glRotatef(90, -1, 0, 0)
        self.draw_tool()

        glPopMatrix()

    def drawEnv(self):
        glPushMatrix()
        glEnable(GL_BLEND)
        self.setupColor([175 / 255, 58 / 255.0, 35 / 255])
        #glRotatef(180, 0, 0, 1);
        self.modelplatform.draw()
        glPopMatrix()

    def drawBox(self):
        glPushMatrix()
        glEnable(GL_BLEND)
        self.setupColor([219 / 255, 77 / 255.0, 46 / 255])
        #glRotatef(180, 0, 0, 1);
        self.modelboxes.draw()
        glPopMatrix()

    def drawGL(self):
        #logging.debug("drawGL - redrawing Grid and Robot")

        if self.isDrawGrid:
            self.drawGrid()
        if self.isDrawEnv:
            self.drawEnv()
        if self.isDrawBox:
            self.drawBox()

        self.draw_robot()

    def paintGL(self):
        #print("painting gl")
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glPushMatrix()
        glTranslate(0, 0, self.z_zoom)
        glTranslate(self.xTran, self.yTran, 0)
        glRotated(self.xRot/16.0, 1.0, 0.0, 0.0)
        glRotated(self.yRot/16.0, 0.0, 1.0, 0.0)
        glRotated(self.zRot/16.0, 0.0, 0.0, 1.0)
        glRotated(+90.0, 1.0, 0.0, 0.0)
        self.drawGL()
        self.DrawPoint([0/255, 0/255, 255.0/255.0], 15)
        self.DrawCoords([255.0 / 255, 255.0 / 255, 255.0 / 255.0], 4)
        # self.makePointObject(1)
        glPopMatrix()
        # self.update() # dont do this otherwise it will update multiple times a second

    def DrawPoint(self, color, size):
        #print("drawPoint")
        #print(self.specialPoints)
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, self.color);
        glPointSize(size);
        for i,p in enumerate(self.specialPoints):
            glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0, 0, 1.0]);
            glBegin(GL_POINTS);
            glVertex3f(p[0], p[1], p[2])
            glEnd()

            """if self.color[i] == 1:
                glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [1.0, 1.0, 1.0]);
                glBegin(GL_POINTS);
                glVertex3f(self.listPoints[i][0], self.listPoints[i][1], self.listPoints[i][2])
                glVertex3f(self.listPoints[i+1][0], self.listPoints[i+1][1], self.listPoints[i+1][2])
                glEnd()"""
        glPopMatrix()

    def DrawCoords(self, color, size):
        #print("draw coords")

        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, self.color);
        glLineWidth(size)
        glPointSize(size);
        for i in np.arange(len(self.listCoords)-1):
            if i == 0:
                continue
            # if self.color[i] == 1:
            glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0, 0, 0]);
            glBegin(GL_LINES);
            glVertex3f(self.listCoords[i][0], self.listCoords[i][1], self.listCoords[i][2])
            glVertex3f(self.listCoords[i+1][0], self.listCoords[i+1][1], self.listCoords[i+1][2])
            glEnd()
        glPopMatrix()

    def loadSVG(self,block,size):
        # DONE? TODO: make a new method that just updates and doesnt need to reload the entire file
        block.update()
        print("loading svg")
        self.listCoords = np.array([[0,0,0]])
        self.specialPoints = np.array([[0, 0, 0]])

        glPushMatrix()
        coordinates = block.coordinates_travel

        csys = m3d.Transform(block.csys)
        csys_vector = csys.pose_vector
        self.specialPoints = np.append(self.specialPoints,[csys_vector[:3]],axis=0)

        for i, path in enumerate(coordinates):
            #print("loading path",i,path)
            for j,coord in enumerate(path):
                #print(coord)
                #csys = m3d.Transform(block.csys)
                t = csys * m3d.Transform(coord)
                pose = t.pose_vector
                #print("pose", pose)
                self.listCoords = np.append(self.listCoords,[pose[:3]],axis=0)
                #print(j,"listCoords:", self.listCoords)

        #print("listCoords:", self.listCoords)
        glPopMatrix()

    def makePointObject(self,block):
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, self.color);
        #print("make points")
        #genList = glGenLists(1)
        #glNewList(genList, self.gl.GL_COMPILE)

        #glClearColor(0, 0, 1, 1)
        #glColor3f(0.40, 0.0, 1.0)
        glPointSize(20)
        glBegin(GL_POINTS)
        self.setupColor([105.0 / 255, 180.0 / 255, 0 / 255])
        #glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [1.0, 1.0, 1.0]);
        #glColor3f(0.40, 1, 1.0)
        glVertex3f(0,0,0)
        glVertex3f(100,10,10)
        glVertex3f(50,500,500)
        glVertex3f(100,100,1000)
        glEnd()

        #self.drawGL()
        glPopMatrix()
        #self.update()

        #self.gl.glEnd()
        #self.gl.glEndList()
        #return genList

    def resizeGL(self, width, height):
        #print("resize")

        side = min(width, height)
        if side < 0:
            return
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        GLU.gluPerspective(35.0, width / float(height), 1.0, 20000.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslated(0.0, 0.0, -40.0)


    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def drawGrid(self):
        glLineWidth(1)
        glPushMatrix()
        #print("drawing grid")
        # color = [255.0/255, 57.0/255, 0.0/255]
        color = [255/255, 162/255, 162.0/255]
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, color);
        step = 100
        num = 10
        for i in arange(-num, num+1):
            glBegin(GL_LINES)
            glVertex3f(i*step, -num * step, 0)
            glVertex3f(i*step, num*step, 0)
            glVertex3f(-num * step, i*step, 0)
            glVertex3f(num*step, i*step, 0)
            glEnd()
        glPopMatrix()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()
        if event.buttons() & QtCore.Qt.LeftButton:
            self.setXRotation(self.xRot + 4 * dy)
            self.setYRotation(self.yRot - 4 * dx)
        elif event.buttons() & QtCore.Qt.RightButton:
            self.setZoom(self.z_zoom + 5.0*dy)
        elif event.buttons() & QtCore.Qt.MidButton:
            self.setXYTranslate(dx, dy)
        self.lastPos = event.pos()


    def setupColor(self, color):
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, color);

    def xRotation(self):
        return self.xRot

    def yRotation(self):
        return self.yRot

    def zRotation(self):
        return self.zRot

    def normalizeAngle(self, angle):
        while (angle < 0):
            angle += 360 * 16
        while (angle > 360 * 16):
            angle -= 360 * 16