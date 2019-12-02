from PyQt5.QtWidgets import *


class NodeEditorWnd(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.initUi()

    def initUi(self):

        self.setGeometry(300,300,600,600)
        self.setWindowTitle("node editor")

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        self.grScene = QGraphicsScene()

        self.view = QGraphicsView(self)
        self.view.setScene(self.grScene)
        self.layout.addWidget(self.view)

        self.show()