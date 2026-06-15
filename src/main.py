import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel
from PySide6 import QtWidgets
from PySide6.QtCore import Qt




if __name__ == "__main__":
    n = len(sys.argv)
    args = sys.argv
    
    # i.e., no arguements were passed
    if n == 1:
        app = QtWidgets.QApplication(sys.argv)
        
        window = QtWidgets.QPushButton("Hello world!")
        window.show()
        
        scene = QtWidgets.QGraphicsScene()
        scene.addText("whatsup")
        view = QtWidgets.QGraphicsView(scene)
        view.show()
        
        app.exec()
    
    for arg in range(1, n):
        print(arg)
    