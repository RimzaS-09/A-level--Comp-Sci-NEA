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

from PySide6.QtCore import Slot, Signal

class MapWidget(QWidget):
    def __init__(self, map_centre: tuple):
        super().__init__()

        self.tiles = []
        self.viewport = Viewport( (map_centre[0], map_centre[1]), map_centre[2])
        self.renderer = MapRenderer()
        
        self.viewport_changed = Signal(Viewport)

    
    def paintEvent(self, event: QtGui.QPaintEvent) -> None:  
        painter = QPainter(self)
        self.renderer.render_map(self.tiles, self.viewport, painter)
        return super().paintEvent(event)
    
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.beginning_position = event.position()
        return super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        
        new_position = event.position()
        
        dx = new_position.x() - self.beginning_position.x()
        dy = new_position.y() - self.beginning_position.y()
        self.viewport.pan(dx, dy)
        
        self.beginning_position = new_position
        
        self.update()
        return super().mouseMoveEvent(event)
    
    def wheelEvent(self, event: QWheelEvent) -> None:
        scroll_delta = event.angleDelta().y()
        scroll_delta = int(scroll_delta / 120)
        
        mouse = event.position()
        
        print("Mouse position at: ", mouse.toTuple())
        self.viewport.zoom_to_point(mouse.x(), mouse.y(), scroll_delta)
        self.update()
        print(self.viewport.get_centre())
        return super().wheelEvent(event)
    
    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        new_screen_size = event.size()
        self.viewport.set_screen_size(new_screen_size.toTuple())
        self.update()
        return super().resizeEvent(event)

    @Slot(list)
    def set_tiles(self, tiles):
        self.tiles = tiles
        self.update()
    
