import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUi

import sys, os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, currentdir)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
##grandparentdir =  os.path.dirname(parentdir)
##sys.path.insert(0, grandparentdir)
##g_g_parentdir = os.path.dirname(grandparentdir)
##sys.path.insert(0, g_g_parentdir)

import title_rc
from main_paras import getMainTopLeft

class _WrongPassword(QtWidgets.QDialog):
    def __init__(self,parent=None):
        super(_WrongPassword, self).__init__(parent)


        loadUi(os.path.join(currentdir,'wrong_password.ui'),self)
        self.config()
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup)
        self.setWindowFlags(flags)
        

    def closeEvent(self,event):
        print("_WrongPassword is closing")
    def setMessage(self,message, button=None):
        #print('in setMessage',message,button)
        self.title.setText(message)
        if(button!=None):
            self.try_bt.setText(button)

    def config(self):
        try:
            self.try_bt.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.try_bt.clicked.connect(self.try_bt_hook)
            pass
        except Exception as error:
            print(error)

    def try_bt_hook(self):
        try:
            self.close()
            pass
        except Exception as error:
            print(error)

if __name__ == "__main__":
    from PyQt5.QtCore import QTranslator
    import sys
##    trans=QTranslator()
##    trans.load("setting_wrap.qm")
    

    
    app = QtWidgets.QApplication(sys.argv)
##    app.installTranslator(trans)

    QtWidgets.QMainWindow
    window=_WrongPassword()
    window.show()
    
    rtn= app.exec_()
    print('main app return', rtn)
    sys.exit(rtn)
