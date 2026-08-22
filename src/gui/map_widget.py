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
from map.viewport import Viewport

from PySide6.QtCore import Slot

class MapWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.tiles = []
        self.viewport = Viewport(0, 0)
        self.renderer = MapRenderer()

    @Slot(list)
    def set_tiles(self, tiles):
        self.tiles = tiles
        self.update()