from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer

class BlinkingCursor(QtWidgets.QFrame):
    def __init__(self, index, objectName, parentLayout, parentWidget, parent=None):
        QtWidgets.QFrame.__init__(self, parent)
        self.setFrameShape(QtWidgets.QFrame.VLine)
        self.setStyleSheet(r"QFrame { color: transparent; }")
        # self.setStyleSheet(r"QFrame { color: #86C67C; }")
        self.setLineWidth(2)
        self.setObjectName(objectName)

        self.index = index
        self.parentLayout = parentLayout
        self.parentWidget = parentWidget
        self.visible = False
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.blink)
        self.flashState = 1
    
    def setSelected(self, visible=True):
        self.visible = visible
        if self.visible:
            self.setStyleSheet(r"QFrame { color: #86C67C; }")
            self.flashState = 1
            self.timer.start(530)
        else:
            self.flashState = 0
            self.timer.stop()
            self.setStyleSheet(r"QFrame { color: transparent; }")
    
    def blink(self):
        if self.visible:
            if self.flashState == 0:
                self.flashState = 1
                self.setStyleSheet(r"QFrame { color: #86C67C; }")
            elif self.flashState == 1:
                self.flashState = 0
                self.setStyleSheet(r"QFrame { color: transparent; }")
        else:
            if self.flashState == 1:
                self.flashState = 0
                self.setStyleSheet(r"QFrame { color: transparent; }")
