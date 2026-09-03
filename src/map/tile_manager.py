from PySide6.QtWidgets import QWidget
from PySide6.QtCore import (
    QObject,
    QRunnable,
    QThreadPool,
    Signal,
    Slot,
)
from PySide6.QtGui import QImage
import threading

from database_handling.sql_queries import MBTileDatabase

from models import TileKey, RenderedTile
from map.renderer import TileRenderer



class TileSignal(QObject):
    finished = Signal(
        RenderedTile
    )
    


class TileWorker(QRunnable):
    """
    Class for rendering a single tile.
    
    To be used per thread by TileManager
    """
    def __init__(self, raw_tile):
        super().__init__()
        
        self.raw_tile = raw_tile
        self.signal = TileSignal()
        self.renderer = TileRenderer()
    
    def run(self) -> None:
        result = self.renderer.render_tile(self.raw_tile)
        self.signal.finished.emit(result)


class TileManager(QObject):
    tiles_changed = Signal(RenderedTile)
    
    def __init__(self, database: MBTileDatabase):
        super().__init__()
        self.database = database
        
    
    @Slot(RenderedTile)
    def add_tile(self, tile):
        self.tiles_rendered.append(tile)
        self.tiles_changed.emit(self.tiles_rendered)
        

    @Slot(tuple)
    def update_viewport(self, view_area):
        tiles_to_render = []
        self.tiles_rendered = []

        zoom = view_area[0]
        coord_area = view_area[1]

        threadpool = QThreadPool()

        for x in range(int(coord_area[0]), int(coord_area[1]+1)):
            for y in range(int(coord_area[2]), int(coord_area[3] + 1)):

                tile = self.database.get_tile(zoom, y, x)
                tiles_to_render.append(tile)

        for tile in tiles_to_render:
            worker = TileWorker(tile)
            worker.signal.finished.connect(self.add_tile)
            threadpool.start(worker)