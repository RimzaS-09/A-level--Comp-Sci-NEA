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
        self.viewport = Viewport((0,0), 0)
        self.renderer = MapRenderer()
        
        self.last_position = None
    
    def paintEvent(self, event: QtGui.QPaintEvent) -> None:  
        painter = QPainter(self)
        self.renderer.render_map(self.tiles, self.viewport, painter)
        return super().paintEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if not self.last_position:
            self.last_position = event.position()
            return
        
        new_position = event.position()
        
        dx = new_position.x() - self.last_position.x()
        dy = new_position.y() - self.last_position.y()
        self.viewport.pan(dx, dy)
        
        self.last_position = new_position
        
        self.update()
        return super().mouseMoveEvent(event)

    @Slot(list)
    def set_tiles(self, tiles):
        self.tiles = tiles
        self.update()