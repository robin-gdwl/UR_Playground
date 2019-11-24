from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel

import sys


class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow,self).__init__()

def window():
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setGeometry(100,100,600,600)
    win.setWindowTitle("OKAY ")

    label = QtWidgets.QLabel(win)
    label.setText("???")

    b1 = QtWidgets.QPushButton(win)
    b1.setText("CLICK ME ")
    b1.clicked.connect(clicked)

    win.show()
    sys.exit(app.exec_())

def clicked():
    print("clicked")


window()