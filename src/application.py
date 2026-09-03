from PySide6.QtWidgets import QApplication, QLabel
from PySide6 import QtWidgets
from PySide6.QtCore import Qt

from database_handling.sql_queries import MBTileDatabase
from map.tile_manager import TileManager
from gui.window import MainWindow

from gui import window
from database_handling.connect import SQLConnection
from database_handling.tile_query import DecodedTile
from database_handling.sql_queries import MBTileDatabase
from utils.vector_tile_parsing import vector_tile_pb2


from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
MAP_DIR = DATA_DIR / "map"

class Application:
    def __init__(self):
        
        self.map_databases: list[MBTileDatabase] = []
        
        for file in (DATA_DIR / "map").iterdir():
            if file.is_file() and str(file).endswith(".mbtiles"):
                self.map_databases.append(MBTileDatabase(str(file)))
                

        self.tile_manager = TileManager(self.map_databases[0])
        
        map_centre = self.map_databases[0].get_centre()
        self.window = MainWindow(map_centre)
        


        # Connect application components
        self.window.map_widget.viewport.tiles_in_viewport.connect( self.tile_manager.update_viewport )
        self.tile_manager.tiles_changed.connect( self.window.map_widget.set_tiles )

    def run(self):
        self.window.show()