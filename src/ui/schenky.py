import sys
import popplerqt5
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from ui import mainwindow, mainwindow2, notebutton, blinkingcursor
from model.score import Score
from model.note import Note
from model.skip import Skip
from model.staff import Staff
from model.voice import Voice
from model.constants import NoteName, MinorAccidentals, MajorAccidentals, VoiceType, Clef
from .constants import InputMode


# class Ui_MainWindow(QtWidgets.QMainWindow, mainwindow.Ui_Schenky):
class Ui_Schenky(QtWidgets.QMainWindow, mainwindow2.Ui_MainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent=parent)
        self.setupUi(self)
        self.globalVarsInit()

        #Connect 
        QtWidgets.qApp.focusChanged.connect(self.onFocusChanged)
        self.measureInputWidget.installEventFilter(self)
        self.trebleInputWidget.installEventFilter(self)
        self.bassInputWidget.installEventFilter(self)
        self.refreshButton.clicked.connect(self.displayPdf)
        self.zoomInButton.clicked.connect(self.zoomIn)
        self.zoomOutButton.clicked.connect(self.zoomOut)
        self.urlinieCheckbox.setDisabled(True)
        self.slurButton.clicked.connect(lambda: self.toggleMode(self.slurButton))
        self.unfoldingButton.clicked.connect(lambda: self.toggleMode(self.unfoldingButton))
        self.beamButton.clicked.connect(lambda: self.toggleMode(self.beamButton))
        self.autoRefreshCheckbox.clicked.connect(self.toggleRefresh)
        self.keySelect.currentTextChanged.connect(lambda: self.changeKey(self.keySelect.currentText()))
        self.actionTogglePropertiesPanel.triggered.connect(self.togglePropertiesPanel)
        self.measurePropertiesTree.itemChanged.connect(lambda item, column: self.changeMeasureNumber(item, column))
        self.actionExit.triggered.connect(lambda: sys.exit())
        self.actionRefreshPreview.triggered.connect(self.displayPdf)

        self.noteNameSelect = QtWidgets.QComboBox()
        self.noteNameSelect.setObjectName("noteNameSelect")
        self.noteNameSelect.setStyleSheet("QComboBox {\n"
                "border: 1px solid transparent;\n"
                "background-color: transparent;\n"
                "selection-background-color: #78ab78\n"
                "}\n"
                )
        [self.noteNameSelect.addItem(i) for i in ["C", "D", "E", "F", "G", "A", "B"]]
        self.notePropertiesTree.setItemWidget(self.notePropertiesTree.topLevelItem(1), 1, self.noteNameSelect)
        self.noteNameSelect.activated.connect(self.changeNoteName)

        self.accidentalSelect = QtWidgets.QComboBox()
        self.accidentalSelect.setObjectName("accidentalSelect")
        self.accidentalSelect.setStyleSheet("QComboBox {\n"
                "border: 1px solid transparent;\n"
                "background-color: transparent;\n"
                "selection-background-color: #78ab78\n"
                "}\n"
                )
        [self.accidentalSelect.addItem(i) for i in ["Double flat", "Flat", "Natural", "Sharp", "Double sharp"]]
        self.accidentalSelect.setCurrentIndex(2)
        self.notePropertiesTree.setItemWidget(self.notePropertiesTree.topLevelItem(2), 1, self.accidentalSelect)
        self.accidentalSelect.activated.connect(self.changeAccidental)

        self.registerSelect = QtWidgets.QComboBox()
        self.registerSelect.setObjectName("registerSelect")
        self.registerSelect.setStyleSheet("QComboBox {\n"
                "border: 1px solid transparent;\n"
                "background-color: transparent;\n"
                "selection-background-color: #78ab78\n"
                "}\n"
                )
        [self.registerSelect.addItem(str(i)) for i in range(0, 10)]
        self.registerSelect.setCurrentIndex(3)
        self.notePropertiesTree.setItemWidget(self.notePropertiesTree.topLevelItem(3), 1, self.registerSelect)
        self.registerSelect.activated.connect(self.changeRegister)

        self.notePropertiesTree.setDisabled(True)
        self.measurePropertiesTree.setDisabled(True)

        for cursors in [self.trebleInputHLayout, self.bassInputHLayout, self.measureInputHLayout]:
            if cursors is self.measureInputHLayout:
                cursorName, widget = "SchenkyCursorMeasure0", self.measureInputWidget
            elif cursors is self.trebleInputHLayout: 
                cursorName, widget = "SchenkyCursorTreble0", self.trebleInputWidget     
            else:
                cursorName, widget = "SchenkyCursorBass0", self.bassInputWidget
            cursor = blinkingcursor.BlinkingCursor(0, cursorName, cursors, widget)
            cursors.addWidget(cursor)
            spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
            cursors.addItem(spacerItem)

        # Override mainwindow.py
        self.previewScrollArea.setWidgetResizable(False)
        self.previewScrollArea.setBackgroundRole(QtGui.QPalette.Dark)
        self.imageLabel = QtWidgets.QLabel()
        self.imageLabel.setGeometry(QtCore.QRect(0, 0, 991, 281))
        self.imageLabel.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)
        self.imageLabel.setObjectName("imageLabel")
        self.previewScrollArea.setWidget(self.imageLabel)
        self.propertiesPanel.setFeatures(QtWidgets.QDockWidget.DockWidgetClosable|QtWidgets.QDockWidget.DockWidgetFloatable|QtWidgets.QDockWidget.DockWidgetMovable|QtWidgets.QDockWidget.DockWidgetVerticalTitleBar)
    
    def globalVarsInit(self):
        self.currentStaffWidget = None
        self.selectedNotes = []
        self.scaleFactor = 1.0
        self.inputMode = InputMode.NONE
        self.autoRefresh = False
        self.trebleInputs = []
        self.bassInputs = []
        self.measureInputs = []
        self.currentCursor = None
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
            self.pdf = None
            return
        self.scaleFactor = 1.0
        self.pdf = pdf

    def displayPdf(self):
        self.loadPdf()
        pdfPage = self.pdf.page(0)
        if not pdfPage:
            return
        image = pdfPage.renderToImage(300, 300, -1, -1, -1, -1)
        if image.isNull():
            return
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
    
    def changeNoteName(self):
        if len(self.selectedNotes) == 1:
            noteName = self.noteNameSelect.currentText()
            note = self.selectedNotes[0].note 
            self.selectedNotes[0].updateNote(noteName, note.accidental, note.register)
    
    def changeAccidental(self):
        if len(self.selectedNotes) == 1:
            accidental = self.accidentalSelect.currentIndex() - 2
            note = self.selectedNotes[0].note
            self.selectedNotes[0].updateNote(note.name, accidental, note.register)

    def changeRegister(self):
        if len(self.selectedNotes) == 1:
            register = int(self.registerSelect.currentText())
            note = self.selectedNotes[0].note 
            self.selectedNotes[0].updateNote(note.name, note.accidental, register)
    
    def changeMeasureNumber(self, item, column):
        if item is self.notePropertiesTree.topLevelItem(0):
            return
        if len(self.selectedNotes) == 1:
            oldMeasureNumber = self.selectedNotes[0].measureNumber
            newMeasureNumber = self.notePropertiesTree.topLevelItem(1).text(1)
            if len(newMeasureNumber) == 0 and not self.measurePropertiesTree.isEnabled():
                return
            print(newMeasureNumber)
            if newMeasureNumber.isdigit() and int(newMeasureNumber) > 0:
                self.selectedNotes[0].updateMeasureNumber(int(newMeasureNumber))
            else:
                self.selectedNotes[0].measureNumberError()
                self.selectedNotes[0].updateMeasureNumber(oldMeasureNumber)
                self.notePropertiesTree.topLevelItem(1).setText(1, str(oldMeasureNumber))

    def togglePropertiesPanel(self):
        self.propertiesPanel.setVisible(not self.propertiesPanel.isVisible())
    
    def toggleRefresh(self):
        self.autoRefresh = not self.autoRefresh
        self.refreshButton.setDisabled(self.autoRefresh)
        self.actionRefreshPreview.setEnabled(not self.autoRefresh)
    
    def toggleMode(self, button):
        if button.isChecked():
            for b in [self.slurButton, self.unfoldingButton, self.beamButton]:
                if button != b and b.isChecked():
                    b.setChecked(False)
            if button is self.slurButton:
                self.inputMode = InputMode.SLURS
            elif button is self.unfoldingButton:
                self.inputMode = InputMode.UNFOLDINGS
            elif button is self.beamButton:
                self.inputMode = InputMode.LINES
        else:
            self.inputMode = InputMode.NONE
        self.urlinieCheckbox.setEnabled(self.beamButton.isChecked())
    
    def checkModeButtons(self):
        if len(self.selectedNotes) > 2:
            self.slurButton.setDisabled(True)
            self.unfoldingButton.setDisabled(True)
        else:
            self.slurButton.setEnabled(True)
            self.unfoldingButton.setEnabled(True)
    
    def getCurrentStaff(self):
        if not self.currentStaffWidget:
            return None
        if self.currentStaffWidget is self.trebleInputWidget:
            return self.trebleInputHLayout
        if self.currentStaffWidget is self.bassInputWidget:
            return self.bassInputHLayout
        if self.currentStaffWidget is self.measureInputWidget:
            return self.measureInputHLayout
    
    def setNotePropertiesTreeText(self, index, column, text):
        self.notePropertiesTree.topLevelItem(index).setText(column, QtCore.QCoreApplication.translate("Schenky", text))

    def setMeasurePropertiesTreeText(self, index, column, text):
        self.measurePropertiesTree.topLevelItem(index).setText(column, QtCore.QCoreApplication.translate("Schenky", text))

    def displayInputProperties(self):
        if len(self.selectedNotes) == 1:
            if type(self.selectedNotes[0].note) == Note:
                if self.inputPropertiesTabWidget.currentWidget() == self.measureTab:
                    self.inputPropertiesTabWidget.setCurrentWidget(self.noteTab)
                self.notePropertiesTree.setEnabled(True)
                self.setNotePropertiesTreeText(0, 1, self.selectedNotes[0].objectName())
                self.noteNameSelect.setCurrentText(self.selectedNotes[0].note.name.upper())
                self.accidentalSelect.setCurrentIndex(self.selectedNotes[0].note.accidental + 2)
                self.registerSelect.setCurrentText(str(self.selectedNotes[0].note.register))
                self.removeAndDisableMeasureProperties()
            elif self.selectedNotes[0].isMeasure:
                if self.inputPropertiesTabWidget.currentWidget() == self.noteTab:
                    self.inputPropertiesTabWidget.setCurrentWidget(self.measureTab)
                if self.selectedNotes[0].measureNumber > 0:
                    self.setMeasurePropertiesTreeText(0, 1, self.selectedNotes[0].objectName())
                    self.setMeasurePropertiesTreeText(1, 1, str(self.selectedNotes[0].measureNumber))
                    self.measurePropertiesTree.setEnabled(True)
                else:
                    self.removeAndDisableMeasureProperties()
                self.removeAndDisableNoteProperties()
            elif type(self.selectedNotes[0].note) == Skip:
                self.removeAndDisableNoteProperties()
        else:
            self.removeAndDisableNoteProperties()
            self.removeAndDisableMeasureProperties()
    
    def removeAndDisableNoteProperties(self):
        if len(self.selectedNotes) == 1 and not self.selectedNotes[0].isMeasure:
            if self.inputPropertiesTabWidget.currentWidget() == self.measureTab:
                self.inputPropertiesTabWidget.setCurrentWidget(self.noteTab)
        self.setNotePropertiesTreeText(0, 1, self.selectedNotes[0].objectName() if len(self.selectedNotes) == 1 and not self.selectedNotes[0].isMeasure else "")
        self.noteNameSelect.setCurrentIndex(0)
        self.accidentalSelect.setCurrentIndex(2)
        self.registerSelect.setCurrentIndex(3)
        self.notePropertiesTree.setDisabled(True)

    def removeAndDisableMeasureProperties(self):
        self.measurePropertiesTree.setDisabled(True)
        if len(self.selectedNotes) == 1 and self.selectedNotes[0].isMeasure:
            if self.inputPropertiesTabWidget.currentWidget() == self.noteTab:
                self.inputPropertiesTabWidget.setCurrentWidget(self.measureTab)
        self.setMeasurePropertiesTreeText(0, 1, self.selectedNotes[0].objectName() if len(self.selectedNotes) == 1 and self.selectedNotes[0].isMeasure else "")
        self.setMeasurePropertiesTreeText(1, 1, "")
    
    def onFocusChanged(self, old, now):
        # if old is self.trebleInputWidget or old is self.bassInputWidget or old is self.measureInputWidget:
        #     old.clearFocus()
        # if now is self.trebleInputWidget or now is self.bassInputWidget or now is self.measureInputWidget:
        #     self.setFocusWidget(now)
        # elif type(now) == notebutton.NoteButton:
        #     self.noteButtonMousePressEvent(now)
        pass
    
    def setFocusWidget(self, widget):
        self.setNoteButton(False)
        self.setActiveStaffWidget(widget)
        if self.notePropertiesTree.isEnabled():
            self.removeAndDisableNoteProperties()
    
    def noteButtonMousePressEvent(self, button, e=None):
        if len(self.selectedNotes) == 1 and type(self.selectedNotes[0].note) == Skip:
            self.setActiveStaffWidget(button.parentWidget)
            self.setNoteButton(button)
            return
        if e and e.modifiers() & Qt.ControlModifier:
            if len(self.selectedNotes) > 0:
                if button.parentWidget == self.selectedNotes[0].parentWidget:
                    if not button.selected:
                        button.setSelected(True)
                        button.setFocus()
                        self.selectedNotes.append(button)
                        self.removeAndDisableNoteProperties()
                        self.setCursor(False)
                        self.checkModeButtons()
                    else:
                        if len(self.selectedNotes) == 1:
                            self.setNoteButton(False)
                            return
                        self.selectedNotes.remove(button)
                        button.setSelected(False)
                        if len(self.selectedNotes) == 1:
                            self.setNoteButton(self.selectedNotes[0])
                            return
                        self.selectedNotes[-1].setFocus()
                        self.checkModeButtons()
                return
        if e and e.modifiers() & Qt.ShiftModifier:
            pass
        self.setActiveStaffWidget(button.parentWidget)
        self.setNoteButton(button)
    
    def mousePressEvent(self, e):
        pos = e.pos()
        child = self.childAt(pos)

        if child is self.measureInputWidget or child is self.trebleInputWidget or child is self.bassInputWidget:
            self.setFocusWidget(child)
            currentStaff = self.getCurrentStaff()
            leftBorderPosition = self.inputScrollArea.x()
            cursors = []
            for i in range(currentStaff.count() - 1):
                w = currentStaff.itemAt(i).widget()
                if type(w) == blinkingcursor.BlinkingCursor:
                    cursors.append(w)
            if len(cursors) == 0:
                return
            cursor = min(cursors, key=lambda y: abs(pos.x() - leftBorderPosition - y.pos().x()))
            self.setCursor(cursor)
        elif type(child) == blinkingcursor.BlinkingCursor:
            self.setFocusWidget(child.parentWidget)
            self.setCursor(child)
    
    def addNote(self, index, objectName, name, hLayout, widget, cursorObjectName):
        if name == "" or name.lower() == "s":
            newNote = Skip()
        else:
            accidental = (MajorAccidentals[self.score.key][NoteName[name]]
                                    if self.score.quality == "major" else MinorAccidentals[self.score.key][NoteName[name]])
            newNote = Note(name, accidental, 3, True)
        isMeasure = False
        if hLayout is self.measureInputHLayout:
            isMeasure = True
        newNoteButton = notebutton.NoteButton(index, objectName, newNote, hLayout, widget, isMeasure=isMeasure, parent=self)

        if hLayout is self.trebleInputHLayout or hLayout is self.bassInputHLayout:
            self.getMainVoice(hLayout).insert(index, newNote)
        
        hBoxIndex = index * 2 + 1
        hLayout.insertWidget(hBoxIndex, newNoteButton)
        cursor = blinkingcursor.BlinkingCursor(index + 1, cursorObjectName, hLayout, widget)
        hLayout.insertWidget(hBoxIndex + 1, cursor)
        for i in range(hBoxIndex + 2, hLayout.count() - 1):
            hLayout.itemAt(i).widget().index += 1
        return newNoteButton

    def getInputList(self, staff):
        if staff is self.trebleInputHLayout or staff is self.trebleInputWidget:
            return self.trebleInputs
        if staff is self.bassInputHLayout or staff is self.bassInputWidget:
            return self.bassInputs
        if staff is self.measureInputHLayout or staff is self.measureInputWidget:
            return self.measureInputs

    def getMainVoice(self, staff):
        if staff is self.trebleInputHLayout or staff is self.trebleInputWidget:
            return self.score.staves[0].main_voice.notes
        if staff is self.bassInputHLayout or staff is self.bassInputWidget:
            return self.score.staves[1].main_voice.notes
        return None
    
    def setNoteButton(self, noteButton):
        [nb.setSelected(False) for nb in self.selectedNotes]
        if noteButton:
            noteButton.setSelected(True)
            noteButton.setFocus()
            self.selectedNotes = [noteButton]
            self.displayInputProperties()
            self.setCursor(False)
        else:
            self.selectedNotes = []
            self.removeAndDisableNoteProperties()
            self.removeAndDisableMeasureProperties()

    def setCursor(self, cursor):
        if self.currentCursor is cursor:
            return
        if self.currentCursor:
            self.currentCursor.setSelected(False)
        if cursor:
            self.currentCursor = cursor
            self.currentCursor.setSelected(True)
            self.setNoteButton(False)
        else:
            self.currentCursor = None
    
    def setActiveStaffWidget(self, widget=False, cursor=False):
        if widget:
            self.currentStaffWidget = widget
        if not self.currentStaffWidget:
            return
        self.currentStaffWidget.setStyleSheet("QWidget { background: #c5e3bf }")
        for staff in [self.trebleInputWidget, self.bassInputWidget, self.measureInputWidget]:
            if staff != self.currentStaffWidget:
                staff.setStyleSheet("")
        self.currentStaffWidget.setFocus()
        if not cursor:
            cursor = self.getCursor()
        self.setCursor(cursor)
    
    def getCursor(self, staff=False, index=-1):
        if not staff:
            staff = self.getCurrentStaff()
        if index == -1:
            index = (staff.count() - 2)/2
        count = 0
        for i in range(staff.count() - 1):
            w = staff.itemAt(i).widget()
            if type(w) == blinkingcursor.BlinkingCursor:
                if count == index:
                    return w
                else:
                    count += 1
        return None

    def getCurrentCursorIndex(self):
        if self.currentCursor:
            staff = self.currentCursor.parentLayout
            count = 0
            for i in range(staff.count() - 1):
                w = staff.itemAt(i).widget()
                if type(w) == blinkingcursor.BlinkingCursor:
                    if w is self.currentCursor:
                        return count
                    else:
                        count += 1
        return None
    
    def eventFilter(self, source, e):
        if e.type() == QtCore.QEvent.KeyPress:
            if source is self.measureInputWidget or source is self.trebleInputWidget or source is self.bassInputWidget:
                if not self.currentStaffWidget:
                    return True
                currentInputList = self.getInputList(self.currentStaffWidget)
                if e.key() == Qt.Key_Left:
                    if len(currentInputList) == 0:
                        return True
                    if len(self.selectedNotes) == 0 and self.currentCursor and self.currentCursor.index > 0:
                        self.noteButtonMousePressEvent(currentInputList[self.currentCursor.index - 1])
                    return True
                if e.key() == Qt.Key_Right:
                    if len(currentInputList) == 0:
                        return True
                    if len(self.selectedNotes) == 0 and self.currentCursor and self.currentCursor.index < len(self.trebleInputs):
                        self.noteButtonMousePressEvent(currentInputList[self.currentCursor.index])
                    return True
                if e.key() == Qt.Key_Up:
                    if self.currentStaffWidget == self.bassInputWidget:
                        self.setActiveStaffWidget(self.trebleInputWidget, self.getCursor(self.trebleInputHLayout, self.currentCursor.index))
                    elif self.currentStaffWidget == self.trebleInputWidget:
                        self.setActiveStaffWidget(self.measureInputWidget, self.getCursor(self.measureInputHLayout, self.currentCursor.index))
                    return True
                if e.key() == Qt.Key_Down:
                    if self.currentStaffWidget == self.measureInputWidget:
                        self.setActiveStaffWidget(self.trebleInputWidget, self.getCursor(self.trebleInputHLayout, self.currentCursor.index))
                    elif self.currentStaffWidget == self.trebleInputWidget:
                        self.setActiveStaffWidget(self.bassInputWidget, self.getCursor(self.bassInputHLayout, self.currentCursor.index))
                    return True
            if source is self.measureInputWidget:
                return True
            if source is self.trebleInputWidget or source is self.bassInputWidget:
                if e.key() not in [Qt.Key_C, Qt.Key_D, Qt.Key_E, Qt.Key_F, Qt.Key_G, Qt.Key_A, Qt.Key_B, Qt.Key_S]:
                    return True
                name = e.text().lower()
                if len(self.selectedNotes) == 0:
                    index = self.currentCursor.index
                    length = len(self.trebleInputs)
                    if self.currentStaffWidget == self.trebleInputWidget:
                        newNoteButton = self.addNote(index, f"SchenkyInputTreble{length}", name, self.trebleInputHLayout, self.trebleInputWidget, f"SchenkyCursorTreble{length + 1}")
                        self.trebleInputs.insert(index, newNoteButton)
                        self.bassInputs.insert(index, self.addNote(index, f"SchenkyInputBass{length}", "", self.bassInputHLayout, self.bassInputWidget, f"SchenkyCursorBass{length + 1}"))
                        self.setCursor(self.getCursor(self.trebleInputHLayout, index + 1))
                    else:
                        newNoteButton = self.addNote(index, f"SchenkyInputBass{length}", name, self.bassInputHLayout, self.bassInputWidget, f"SchenkyCursorBass{length + 1}")
                        self.bassInputs.insert(index, newNoteButton)
                        self.trebleInputs.insert(index, self.addNote(index, f"SchenkyInputTreble{length}", "", self.trebleInputHLayout, self.trebleInputWidget, f"SchenkyCursorTreble{length + 1}"))
                        self.setCursor(self.getCursor(self.bassInputHLayout, index + 1))
                    self.measureInputs.insert(index, self.addNote(index, f"SchenkyInputMeasure{length}", "", self.measureInputHLayout, self.measureInputWidget, f"SchenkyCursorMeasure{length + 1}"))
                return True
        return super(Ui_Schenky, self).eventFilter(source, e)
    
    def noteButtonKeyPressEvent(self, e):
        if not self.currentStaffWidget:
            return
        currentInputList = self.getInputList(self.currentStaffWidget)
        if e.key() == Qt.Key_Delete or e.key() == Qt.Key_Backspace:
            if len(self.selectedNotes) == 1:
                newNote = self.selectedNotes[0].updateNote(None)
                if newNote:
                    if not self.selectedNotes[0].isMeasure:
                        (self.getMainVoice(self.currentStaffWidget))[self.selectedNotes[0].index] = newNote
                    else:
                        self.getMainVoice(self.trebleInputWidget)[self.selectedNotes[0].index].measure = 0
                self.selectedNotes[0].setSelected(True)
                if self.selectedNotes[0].isMeasure:
                    self.removeAndDisableMeasureProperties()
                else:
                    self.removeAndDisableNoteProperties()
        if e.key() == Qt.Key_Left:
            if len(currentInputList) == 0:
                return
            elif len(self.selectedNotes) == 1:
                self.setActiveStaffWidget(self.currentStaffWidget, self.getCursor(self.getCurrentStaff(), self.selectedNotes[0].index))
                self.setNoteButton(False)
            return
        if e.key() == Qt.Key_Right:
            if len(currentInputList) == 0:
                return
            elif len(self.selectedNotes) == 1: 
                self.setActiveStaffWidget(self.currentStaffWidget, self.getCursor(self.getCurrentStaff(), self.selectedNotes[0].index + 1))
                self.setNoteButton(False)
            return
        if e.key() == Qt.Key_Up:
            if e.modifiers() & Qt.ControlModifier:
                if len(self.selectedNotes) == 1 and not self.selectedNotes[0].isMeasure:
                    note = self.selectedNotes[0].note
                    self.selectedNotes[0].updateNote(note.name, note.accidental, note.register + 1)
                    self.displayInputProperties()
                return
            else:
                if len(currentInputList) == 0 or len(self.selectedNotes) != 1:
                    return
                if self.currentStaffWidget == self.bassInputWidget:
                    index = self.selectedNotes[0].index
                    self.setActiveStaffWidget(self.trebleInputWidget)
                    self.setNoteButton(self.trebleInputs[index])
                elif self.currentStaffWidget == self.trebleInputWidget:
                    index = self.selectedNotes[0].index
                    self.setActiveStaffWidget(self.measureInputWidget)
                    self.setNoteButton(self.measureInputs[index])
                return
        if e.key() == Qt.Key_Down:
            if e.modifiers() & Qt.ControlModifier:
                if len(self.selectedNotes) == 1 and not self.selectedNotes[0].isMeasure:
                    note = self.selectedNotes[0].note
                    if note.register > 0:
                        self.selectedNotes[0].updateNote(note.name, note.accidental, note.register - 1)
                    self.displayInputProperties()
                return
            else:
                if len(currentInputList) == 0 or len(self.selectedNotes) != 1:
                    return
                if self.currentStaffWidget == self.measureInputWidget:
                    index = self.selectedNotes[0].index
                    self.setActiveStaffWidget(self.trebleInputWidget)
                    self.setNoteButton(self.trebleInputs[index])
                elif self.currentStaffWidget == self.trebleInputWidget:
                    index = self.selectedNotes[0].index
                    self.setActiveStaffWidget(self.bassInputWidget)
                    self.setNoteButton(self.bassInputs[index])
                return
        if self.currentStaffWidget == self.trebleInputWidget or self.currentStaffWidget == self.bassInputWidget:
            if e.key() not in [Qt.Key_C, Qt.Key_D, Qt.Key_E, Qt.Key_F, Qt.Key_G, Qt.Key_A, Qt.Key_B]:
                return
            if len(self.selectedNotes) == 1:
                name = e.text().lower()
                accidental = (MajorAccidentals[self.score.key][NoteName[name]]
                                    if self.score.quality == "major" else MinorAccidentals[self.score.key][NoteName[name]])
                newNote = self.selectedNotes[0].updateNote(name, accidental)
                if newNote:
                    (self.getMainVoice(self.currentStaffWidget))[self.selectedNotes[0].index] = newNote
                self.displayInputProperties()
                self.selectedNotes[0].setSelected(True)
        if self.currentStaffWidget == self.measureInputWidget:
            if e.key() == Qt.Key_Return or e.key() == Qt.Key_Enter:
                if len(self.selectedNotes) == 1 and self.selectedNotes[0].isMeasure:
                    self.selectedNotes[0].displayMeasureInputDialog()
                    self.displayInputProperties()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui_Schenky()
    ui.show()
    sys.exit(app.exec_())