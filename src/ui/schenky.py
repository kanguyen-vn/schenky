from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import popplerqt5
from ui import mainwindow, notebutton
from model.score import Score
from model.note import Note
from model.skip import Skip
from model.staff import Staff
from model.voice import Voice
from model.constants import NoteName, MinorAccidentals, MajorAccidentals, VoiceType, Clef
from .constants import InputMode


class Ui_MainWindow(QtWidgets.QMainWindow, mainwindow.Ui_Schenky):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent=parent)
        self.setupUi(self)
        
        self.globalVarsInit()
        QtWidgets.qApp.focusChanged.connect(self.onFocusChanged)
        self.refreshButton.clicked.connect(self.displayPdf)
        self.zoomInButton.clicked.connect(self.zoomIn)
        self.zoomOutButton.clicked.connect(self.zoomOut)
        self.urlinieCheckbox.setDisabled(True)
        self.slurButton.clicked.connect(lambda: self.toggleMode(self.slurButton))
        self.unfoldingButton.clicked.connect(lambda: self.toggleMode(self.unfoldingButton))
        self.lineButton.clicked.connect(lambda: self.toggleMode(self.lineButton))
        self.autoRefreshCheckbox.clicked.connect(self.toggleRefresh)
        self.keySelect.currentTextChanged.connect(lambda: self.changeKey(self.keySelect.currentText()))

        self.accidentalSelect = QtWidgets.QComboBox()
        self.accidentalSelect.setObjectName("accidentalSelect")
        self.accidentalSelect.setStyleSheet("QComboBox {\n"
                "border-width: 1px;\n"
                "border-style: solid;\n"
                "border-color: transparent;\n"
                "background-color: transparent;\n"
                "selection-background-color: #78ab78\n"
                "}\n"
                )
        [self.accidentalSelect.addItem(i) for i in ["Double flat", "Flat", "Natural", "Sharp", "Double sharp"]]
        self.accidentalSelect.setCurrentIndex(2)
        self.notePropertiesTable.setCellWidget(2, 1, self.accidentalSelect)
        self.accidentalSelect.activated.connect(self.changeAccidental)

        self.noteNameSelect = QtWidgets.QComboBox()
        self.noteNameSelect.setObjectName("noteNameSelect")
        self.noteNameSelect.setStyleSheet("QComboBox {\n"
                "border-width: 1px;\n"
                "border-style: solid;\n"
                "border-color: transparent;\n"
                "background-color: transparent;\n"
                "selection-background-color: #78ab78\n"
                "}\n"
                )
        [self.noteNameSelect.addItem(i) for i in ["C", "D", "E", "F", "G", "A", "B"]]
        self.notePropertiesTable.setCellWidget(1, 1, self.noteNameSelect)

        self.notePropertiesTable.setDisabled(True)

        # Override mainwindow.py
        self.previewScrollArea.setWidgetResizable(False)
        self.previewScrollArea.setBackgroundRole(QtGui.QPalette.Dark)
        self.imageLabel = QtWidgets.QLabel()
        self.imageLabel.setGeometry(QtCore.QRect(0, 0, 991, 281))
        self.imageLabel.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)
        self.imageLabel.setObjectName("imageLabel")
        self.previewScrollArea.setWidget(self.imageLabel)
    
    def globalVarsInit(self):
        self.currentStaff = None
        self.currentStaffWidget = None
        # self.currentNote = None
        self.selectedNotes = []
        self.scaleFactor = 1.0
        self.inputMode = InputMode.NONE
        self.autoRefresh = False
        self.trebleInputs = []
        self.bassInputs = []
        self.measureInputs = []
        self.pdf = None

        key, quality = "c", "major"
        left = Voice(key, quality, VoiceType.MAIN)
        right = Voice(key, quality, VoiceType.MAIN)
        left_staff = Staff("LH", Clef.BASS, key, quality, left)
        right_staff = Staff("RH", Clef.TREBLE, key, quality, right)
        self.score = Score(key, quality, [right_staff, left_staff])

    def loadPdf(self):
        self.score.engrave()
        pdf = popplerqt5.Poppler.Document.load("output.pdf")
        if not pdf:
            print("Cannot load output.pdf")
            self.pdf = None
            return
        print("Import successful")
        self.scaleFactor = 1.0
        self.pdf = pdf

    def displayPdf(self):
        self.loadPdf()
        pdfPage = self.pdf.page(0)
        if not pdfPage:
            print("Cannot load page")
            return
        print("Page successful")
        image = pdfPage.renderToImage(300, 300, -1, -1, -1, -1)
        if image.isNull():
            print("QImage is null")
            return
        print("QImage successful")
        pixmap01 = QtGui.QPixmap.fromImage(image)
        pixmapImage = QtGui.QPixmap(pixmap01)
        self.imageLabel.setPixmap(pixmapImage)
        self.scaleFactor = 1.0
        # self.previewScrollArea.setVisible(True)
        self.imageLabel.adjustSize()

    def scaleImage(self, factor):
        self.scaleFactor *= factor
        self.imageLabel.resize(self.scaleFactor * self.imageLabel.pixmap().size())
        self.adjustScrollBar(self.previewScrollArea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.previewScrollArea.verticalScrollBar(), factor)
        self.zoomInButton.setEnabled(self.scaleFactor < 3.0)
        self.zoomOutButton.setEnabled(self.scaleFactor > 0.333)
    
    def adjustScrollBar(self, scrollbar, factor):
        scrollbar.setValue(int(factor * scrollbar.value() + (factor - 1) * scrollbar.pageStep() / 2))

    def zoomIn(self):
        self.scaleImage(1.25)

    def zoomOut(self):
        self.scaleImage(0.8)
    
    def changeKey(self, comboBoxText):
        split = comboBoxText.split()
        newKey = split[0][0].lower()
        if len(split[0]) > 1:
            if split[0][1] == "#":
                newKey += "_sharp"
            elif split[0][1] == "b":
                newKey += "_flat"
        newQuality = split[1].lower()
        self.score.changeKey(newKey, newQuality)
    
    def changeAccidental(self):
        accidental = self.accidentalSelect.currentIndex() - 2
        note = self.currentNote.note
        self.currentNote.updateNote(note.name, accidental)
    
    def toggleRefresh(self):
        self.autoRefresh = not self.autoRefresh
        self.refreshButton.setDisabled(self.autoRefresh)
    
    def toggleMode(self, button):
        if button.isChecked():
            for b in [self.slurButton, self.unfoldingButton, self.lineButton]:
                if button != b and b.isChecked():
                    b.setChecked(False)
            if button == self.slurButton:
                self.inputMode = InputMode.SLURS
            elif button == self.unfoldingButton:
                self.inputMode = InputMode.UNFOLDINGS
            elif button == self.lineButton:
                self.inputMode = InputMode.LINES
        else:
            self.inputMode = InputMode.NONE
        self.urlinieCheckbox.setEnabled(self.lineButton.isChecked())

    def changeActiveStaffColor(self):
        if not self.currentStaffWidget:
            return
        self.currentStaffWidget.setStyleSheet("QWidget { background: #c5e3bf }")
        for staff in [self.trebleInputWidget, self.bassInputWidget, self.measureInputWidget]:
            if staff != self.currentStaffWidget:
                staff.setStyleSheet("")

    def setTableText(self, r, c, text):
        item = self.notePropertiesTable.item(r, c)
        if not item:
            item = QtWidgets.QTableWidgetItem()
            item.setText(QtCore.QCoreApplication.translate("Schenky", text))
            self.notePropertiesTable.setItem(r, c, item)
        else:
            item.setText(QtCore.QCoreApplication.translate("Schenky", text))

    def displayProperties(self):
        self.notePropertiesTable.setEnabled(True)
        self.setTableText(0, 1, self.currentNote.objectName())
        self.noteNameSelect.setCurrentText(self.currentNote.note.name.upper())
        self.accidentalSelect.setCurrentIndex(self.currentNote.note.accidental + 2)
        self.setTableText(3, 1, str(self.currentNote.note.register))
    
    def removeAndDisableProperties(self):
        self.setTableText(0, 1, self.currentNote.objectName() if self.currentNote else "")
        self.noteNameSelect.setCurrentIndex(0)
        self.accidentalSelect.setCurrentIndex(2)
        self.setTableText(3, 1, "")
        self.notePropertiesTable.setDisabled(True)
    
    def onFocusChanged(self, old, now):
        if old == self.trebleInputWidget or old == self.bassInputWidget or old == self.measureInputWidget:
            old.clearFocus()
        if now == self.trebleInputWidget or now == self.bassInputWidget or now == self.measureInputWidget:
            self.currentStaffWidget = now
            if self.currentNote:
                self.currentNote.setSelected(False)
            self.currentNote = None
            self.changeActiveStaffColor()
            if self.notePropertiesTable.isEnabled():
                self.removeAndDisableProperties()
        if now == self.trebleInputWidget:
            self.currentStaff = self.trebleInputHLayout
        elif now == self.bassInputWidget:
            self.currentStaff = self.bassInputHLayout
        elif now == self.measureInputWidget:
            self.currentStaff = self.measureInputHLayout
        elif type(now) == notebutton.NoteButton:
            # print("Treble:", self.score.staves[0].main_voice)
            # print("Bass:", self.score.staves[1].main_voice)
            if self.currentNote and self.currentNote != now:
                self.currentNote.setSelected(False)
            self.currentNote = now
            self.currentNote.setSelected(True)
            self.currentStaff = now.parentLayout
            self.currentStaffWidget = now.parentWidget
            self.changeActiveStaffColor()
            if type(now.note) == Note:
                self.displayProperties()
            else:
                self.removeAndDisableProperties()
    
    def addNote(self, index, objectName, name, hLayout, widget):
        if name == "":
            newNote = Skip()
        else:
            accidental = (MajorAccidentals[self.score.key][NoteName[name]]
                                    if self.score.quality == "major" else MinorAccidentals[self.score.key][NoteName[name]])
            newNote = Note(name, accidental, 3, True)
        newNoteButton = notebutton.NoteButton(index, objectName, newNote, hLayout, widget, self.keyPressEvent)

        if hLayout == self.trebleInputHLayout or hLayout == self.bassInputHLayout:
            self.getMainVoice(hLayout).append(newNote)
        count = hLayout.count()
        if count > 1:
            hLayout.removeItem(hLayout.itemAt(count - 1))
        hLayout.addWidget(newNoteButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        hLayout.addItem(spacerItem)
        return newNoteButton

    def getInputList(self, staff):
        if staff == self.trebleInputHLayout or staff == self.trebleInputWidget:
            return self.trebleInputs
        if staff == self.bassInputHLayout or staff == self.bassInputWidget:
            return self.bassInputs
        if staff == self.measureInputHLayout or staff == self.measureInputWidget:
            return self.measureInputs

    def getMainVoice(self, staff):
        if staff == self.trebleInputHLayout or staff == self.trebleInputWidget:
            return self.score.staves[0].main_voice.notes
        if staff == self.bassInputHLayout or staff == self.bassInputWidget:
            return self.score.staves[1].main_voice.notes
        return None
    
    def keyPressEvent(self, e):
        if self.currentStaff == None:
            return
        currentInputList = self.getInputList(self.currentStaff)
        if e.key() == Qt.Key_Left:
            if len(currentInputList) == 0:
                return
            if not self.currentNote:
                self.currentNote = currentInputList[-1]
            elif self.currentNote.index > 0:
                self.currentNote = self.getInputList(self.currentNote.parentLayout)[self.currentNote.index - 1]
            self.currentNote.setFocus()
            return
        if e.key() == Qt.Key_Right:
            if len(currentInputList) == 0:
                return
            if not self.currentNote:
                self.currentNote = currentInputList[0]
            elif self.currentNote.index < len(self.trebleInputs) - 1:
                self.currentNote = self.getInputList(self.currentNote.parentLayout)[self.currentNote.index + 1]
            self.currentNote.setFocus()
            return
        if e.key() == Qt.Key_Up:
            if e.modifiers() & Qt.ControlModifier:
                note = self.currentNote.note
                self.currentNote.updateNote(note.name, note.accidental, note.register + 1)
                self.displayProperties()
                return
            else:
                if len(currentInputList) == 0 or not self.currentNote:
                    return
                if self.currentStaff == self.bassInputHLayout:
                    self.currentNote = self.trebleInputs[self.currentNote.index]
                elif self.currentStaff == self.trebleInputHLayout:
                    self.currentNote = self.measureInputs[self.currentNote.index]
                self.currentNote.setFocus()
                return
        if e.key() == Qt.Key_Down:
            if e.modifiers() & Qt.ControlModifier:
                note = self.currentNote.note
                if note.register > 0:
                    self.currentNote.updateNote(note.name, note.accidental, note.register - 1)
                self.displayProperties()
                return
            else:
                if len(currentInputList) == 0 or not self.currentNote:
                    return
                if self.currentStaff == self.measureInputHLayout:
                    self.currentNote = self.trebleInputs[self.currentNote.index]
                elif self.currentStaff == self.trebleInputHLayout:
                    self.currentNote = self.bassInputs[self.currentNote.index]
                self.currentNote.setFocus()
                return
        if self.currentStaff == self.trebleInputHLayout or self.currentStaff == self.bassInputHLayout:
            if e.key() == Qt.Key_C:
                name = "c"
            elif e.key() == Qt.Key_D:
                name = "d"
            elif e.key() == Qt.Key_E:
                name = "e"
            elif e.key() == Qt.Key_F:
                name = "f"
            elif e.key() == Qt.Key_G:
                name = "g"
            elif e.key() == Qt.Key_A:
                name = "a"
            elif e.key() == Qt.Key_B:
                name = "b"
            else:
                return
            if not self.currentNote:
                index = len(self.trebleInputs)
                if self.currentStaff == self.trebleInputHLayout:
                    self.trebleInputs.append(self.addNote(index, f"SchenkyInputTreble{index}", name, self.trebleInputHLayout, self.trebleInputWidget))
                    self.bassInputs.append(self.addNote(index, f"SchenkyInputBass{index}", "", self.bassInputHLayout, self.bassInputWidget))
                else:
                    self.bassInputs.append(self.addNote(index, f"SchenkyInputBass{index}", name, self.bassInputHLayout, self.bassInputWidget))
                    self.trebleInputs.append(self.addNote(index, f"SchenkyInputTreble{index}", "", self.trebleInputHLayout, self.trebleInputWidget))
                self.measureInputs.append(self.addNote(index, f"SchenkyInputMeasure{index}", "", self.measureInputHLayout, self.measureInputWidget))
            else:
                accidental = (MajorAccidentals[self.score.key][NoteName[name]]
                                    if self.score.quality == "major" else MinorAccidentals[self.score.key][NoteName[name]])
                newNote = self.currentNote.updateNote(name, accidental)
                if newNote:
                    (self.getMainVoice(self.currentStaff))[self.currentNote.index] = newNote
                self.displayProperties()
                # self.currentNote.note.updateNote(name, accidental)
        if self.currentStaff == self.measureInputWidget:
            pass


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui_MainWindow()
    ui.show()
    sys.exit(app.exec_())