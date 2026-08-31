from PySide6 import QtWidgets as pyqt
from PySide6.QtCore import Qt, QPoint
from PySide6.QtCore import QSize
from PySide6 import QtGui
from PySide6 import QtCore
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel
from PySide6.QtGui import QPixmap, QColorConstants, QPainter
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QPainter, QMouseEvent, QWheelEvent
from PySide6.QtWidgets import QWidget

from map.renderer import MapRenderer
from gui.map_widget import MapWidget

class MainWindow (pyqt.QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("A-Level NEA")
        
        self.setMinimumSize(720, 480)
        
        self.map_widget = MapWidget()
        self.setCentralWidget(self.map_widget)
        
        self.create_menu()
        
        self.show()
    
    def create_menu(self):
        top_menu = self.menuBar()
        file_menu = top_menu.addMenu("File")
        load_menu = file_menu.addMenu("Load")
        
        top_menu.addSeparator()
        
        new_route_button = top_menu.addMenu("New route")



        
        
        
        
        