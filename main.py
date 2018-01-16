import sys
from PyQt5 import QtWidgets
from components import Database as db
from components import Main

if __name__ == '__main__':
    if not db.checkSetup():
        db.setup()
        print('Setting up...')
    app = QtWidgets.QApplication(sys.argv)
    parent = QtWidgets.QMainWindow()
    Main.MainWindow(parent)
    parent.show()
    sys.exit(app.exec_())