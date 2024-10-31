import sys

from app import MainWindow
from login import LoginWindow
from PySide6 import QtCore, QtWidgets

global userID
def main():
    logIn=QtWidgets.QApplication(sys.argv)
    logIn.setApplicationName('登录')
    loginWindow=LoginWindow()
    loginWindow.show()
    loginWindow.raise_()
    sys.exit(logIn.exec_())



if __name__ == '__main__':
    main()