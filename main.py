from PyQt5 import QtWidgets
from components import Database as db
from containers import Main
import sys

# Entry point for application
if __name__ == '__main__':
    if not db.checkSetup():
        db.setup()
    app = QtWidgets.QApplication(sys.argv)
    parent = QtWidgets.QMainWindow()
    Main.MainWindow(parent)
    parent.show()
    sys.exit(app.exec_())
