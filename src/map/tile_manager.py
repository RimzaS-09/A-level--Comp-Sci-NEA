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



class TileSignal(QObject):
    finished = Signal(
        TileKey,
        QImage
    )
    


class TileWorker(QRunnable):
    """
    Class for rendering a single tile.
    
    To be used per thread by TileManager
    """
    def __init__(self, database, tile_coords):
        self.database = database
        self.tile_coords = tile_coords
    
    def run(self) -> None:
        pass


class TileManager(QObject):
    tiles_changed = Signal(list[RenderedTile])
    
    def __init__(self, database: MBTileDatabase):
        database.get_tiles_of_zoomlevel(0)
        
        

    @Slot(tuple)
    def update_viewport(self, view_area):
        pass