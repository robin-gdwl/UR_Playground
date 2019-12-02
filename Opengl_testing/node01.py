import sys

from PyQt5.QtWidgets import *

from Opengl_testing.node_editor_wnd import NodeEditorWnd

if __name__ == '__main__':
    app = QApplication(sys.argv)

    wnd = NodeEditorWnd()

    sys.exit(app.exec_())
