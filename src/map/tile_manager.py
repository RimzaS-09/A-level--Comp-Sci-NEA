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

from models import TileKey



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


class TileManager:
    def __init__(self, database: MBTileDatabase):
        pass
    
