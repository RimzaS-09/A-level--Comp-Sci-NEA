from PySide6 import QtWidgets as pyqt
from PySide6.QtCore import Qt
from PySide6 import QtGui


class MainWindow (pyqt.QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("A-Level NEA")
        label = pyqt.QLabel("Hello there!")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.setMinimumSize(720, 480)
        
        self.setCentralWidget(label)
        self.create_menu()
    
    def create_menu(self):
        top_menu = self.menuBar()
        file_menu = top_menu.addMenu("File")
        load_menu = file_menu.addMenu("Load")
        
        top_menu.addSeparator()
        
        new_route_button = top_menu.addMenu("New route")
        

app = pyqt.QApplication()

window = MainWindow()
window.show()

app.exec()
        