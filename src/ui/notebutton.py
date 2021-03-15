from PyQt5 import QtCore, QtGui, QtWidgets
from model.skip import Skip
from model.note import Note
from model.constants import Accidental

class NoteButton(QtWidgets.QPushButton):
    def __init__(self, index, objectName, note, parentLayout, parentWidget, isMeasure=False, parent=None):
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
        self.parent = parent
        
        # New variables
        self.parentLayout = parentLayout
        self.parentWidget = parentWidget
        self.index = index
        self.note = note
        self.selected = False
        self.isMeasure = isMeasure
        self.measureNumber = 0
        self.display()

    def updateNote(self, name=None, accidental=-3, register=None):
        if not name:
            self.note = Skip()
            if self.isMeasure:
                self.measureNumber = 0
        else:
            if type(self.note) == Skip:
                self.note = Note(name, accidental if accidental else Accidental["natural"], register if register else 3, True)
            else:
                self.note.name = name
                if 2 >= accidental >= -2:
                    self.note.accidental = accidental
                if register:
                    self.note.register = register
        self.display()
        return self.note

    def setSelected(self, selected):
        self.selected = selected
        self.display()
    
    def display(self):
        if self.isMeasure:
            if self.measureNumber <= 0:
                if not self.selected:
                    self.setStyleSheet("QPushButton { border: 1px solid transparent; }\n")
                else:
                    self.setStyleSheet("QPushButton { border: 1px solid transparent; background-color: #86C67C; }\n")
                self.setText(QtCore.QCoreApplication.translate("Schenky", ""))
            elif self.measureNumber > 0:
                if not self.selected:
                    self.setStyleSheet("QPushButton { border: 1px solid black; }\n")
                else:
                    self.setStyleSheet("QPushButton { border: 1px solid black; background-color: #86C67C; }\n")
                self.setText(QtCore.QCoreApplication.translate("Schenky", str(self.measureNumber)))
        elif type(self.note) == Skip:
            if not self.selected:
                self.setStyleSheet("QPushButton { border: 1px solid transparent; }\n")
            else:
                self.setStyleSheet("QPushButton { border: 1px solid transparent; background-color: #86C67C; }\n")
            self.setText(QtCore.QCoreApplication.translate("Schenky", ""))
        else:
            if not self.selected:
                self.setStyleSheet("QPushButton { border: 1px solid black; }\n")
            else:
                self.setStyleSheet("QPushButton { border: 1px solid black; background-color: #86C67C; }\n")
            self.setText(QtCore.QCoreApplication.translate("Schenky", str(self.note)))

    def keyPressEvent(self, e):
        self.parent.noteButtonKeyPressEvent(e)
    
    def mousePressEvent(self, e):
        self.parent.noteButtonMousePressEvent(self, e)

    def updateMeasureNumber(self, measureNumber):
        self.measureNumber = measureNumber
        self.parent.getMainVoice(self.parent.trebleInputHLayout)[self.index].measure = measureNumber
        self.display()

    def measureNumberError(self):
        errorBox = QtWidgets.QMessageBox(parent=self.parent if self.parent else None)
        errorBox.setIcon(QtWidgets.QMessageBox.Warning)
        errorBox.setWindowTitle("Format Error")
        errorBox.setText("Measure number has to be a positive integer.")
        errorBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        errorBox.exec()

    def displayMeasureInputDialog(self, e=None):
        text, ok = QtWidgets.QInputDialog.getText(self.parent if self.parent else None, "Measure number", "Enter measure number:")
        if ok:
            if text.isdigit() and int(text) > 0:
                self.updateMeasureNumber(int(text))
            else:
                self.measureNumberError()

    def mouseDoubleClickEvent(self, e):
        if not self.isMeasure:
            self.mousePressEvent(e)
        else:
            self.displayMeasureInputDialog(e)
            
            