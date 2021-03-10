from PyQt5 import QtCore, QtGui, QtWidgets
from model.skip import Skip
from model.note import Note
from model.constants import Accidental

class NoteButton(QtWidgets.QPushButton):
    def __init__(self, index, objectName, note, parentLayout, parentWidget, parentKeyPress, parent=None):
        QtWidgets.QPushButton.__init__(self, parent)
        self.setMinimumSize(QtCore.QSize(40, 0))
        self.setMaximumSize(QtCore.QSize(40, 16777215))
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.setCheckable(False)
        self.setChecked(False)
        self.setAutoDefault(False)
        self.setDefault(False)
        self.setFlat(True)
        self.setObjectName(objectName)
        
        # New variables
        self.parentLayout = parentLayout
        self.parentWidget = parentWidget
        self.index = index
        self.note = note
        self.parentKeyPress = parentKeyPress
        self.selected = False
        self.display()

    def updateNote(self, name=None, accidental=None, register=None):
        if not name:
            self.note = Skip()
        else:
            if type(self.note) == Skip:
                self.note = Note(name, accidental if accidental else Accidental["natural"], register if register else 3, True)
                return self.note
            else:
                self.note.name = name
                if accidental:
                    self.note.accidental = accidental
                if register:
                    self.note.register = register
        self.display()
        return None

    def setSelected(self, selected):
        self.selected = selected
        self.display()
    
    def display(self):
        if type(self.note) == Skip:
            if not self.selected:
                # self.setStyleSheet("QPushButton {\n"
                #     "border-width: 1px;\n"
                #     "border-style: solid;\n"
                #     "border-color: transparent;\n"
                #     "}\n"
                #     "QPushButton:focus {\n"
                #     "background-color: #86C67C\n"
                #     "}\n")
                self.setStyleSheet("QPushButton {\n"
                    "border-width: 1px;\n"
                    "border-style: solid;\n"
                    "border-color: transparent;\n"
                    "}\n")
            else:
                self.setStyleSheet("QPushButton {\n"
                    "border-width: 1px;\n"
                    "border-style: solid;\n"
                    "border-color: transparent;\n"
                    "background-color: #86C67C;\n"
                    "}\n")
            self.setText(QtCore.QCoreApplication.translate("Schenky", ""))
            self.skip = True
        else:
            if not self.selected:
                # self.setStyleSheet("QPushButton {\n"
                #     "border-width: 1px;\n"
                #     "border-style: solid;\n"
                #     "border-color: black;\n"
                #     "}\n"
                #     "QPushButton:focus {\n"
                #     "background-color: #86C67C\n"
                #     "}\n")
                self.setStyleSheet("QPushButton {\n"
                    "border-width: 1px;\n"
                    "border-style: solid;\n"
                    "border-color: black;\n"
                    "}\n")
            else:
                self.setStyleSheet("QPushButton {\n"
                    "border-width: 1px;\n"
                    "border-style: solid;\n"
                    "border-color: black;\n"
                    "background-color: #86C67C;\n"
                    "}\n")
            self.setText(QtCore.QCoreApplication.translate("Schenky", str(self.note)))
            self.skip = False

    def keyPressEvent(self, e):
        self.parentKeyPress(e)
        