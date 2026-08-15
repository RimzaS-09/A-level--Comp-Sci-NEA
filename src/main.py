import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel
from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from gui import window



if __name__ == "__main__":
    n = len(sys.argv)
    args = sys.argv
    
    # i.e., no arguements were passed

    app = QtWidgets.QApplication(sys.argv)
    
    window = window.MainWindow()
    window.create_menu()
    window.show()
    
    app.exec()
    