import sys
from PyQt5 import QtWidgets
from ui import schenky

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    # ui = schenky.Ui_MainWindow()
    ui = schenky.Ui_Schenky()
    ui.show()
    sys.exit(app.exec_())