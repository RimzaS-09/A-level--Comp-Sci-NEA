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


# A typedef to shorten a tuple containing tile metadata
# (zoom, column, row)
TileKey = tuple[int, int, int]


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
        self.database.new_connection(threading.get_ident())
        self.database.switch_thread_to(threading.get_ident())
        
        data = self.database.get_tile_data(*self.tile_coords)
        run_function_on_data(data)  # Just as an example


class TileManager:
    def __init__(self, database: MBTileDatabase):
        pass
    
