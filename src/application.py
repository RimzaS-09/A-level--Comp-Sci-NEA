from database_handling.sql_queries import MBTileDatabase
from map.tile_manager import TileManager
from gui.window import MainWindow
from PySide6.QtWidgets import QApplication

from database_handling.sql_queries import MBTileDatabase


from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
MAP_DIR = DATA_DIR / "map"

class Application(QApplication):
    """User defined wrapper around QApplication"""
    def __init__(self, args):
        super().__init__(args)
        
        ## TODO: The current implementation works by getting a list of all MBTile maps in the map directory
        ## But only loads in the first one.
        ## In future revisions, allow for multiple MBTile maps to load simultaneously
        self.map_databases: list[MBTileDatabase] = []   # NOTE: Also, this maplist can be a linkedlist

        # NOTE: could raise error type FileNotFoundError
        for file in (DATA_DIR / "map").iterdir():
            if file.is_file() and str(file).endswith(".mbtiles"):
                self.map_databases.append(MBTileDatabase(str(file)))
                
        # NOTE: could raise error type MapDataNotFoundError
        self.tile_manager = TileManager(self.map_databases[0])
        
        map_centre = self.map_databases[0].get_centre()
        self.window = MainWindow(map_centre)

        # Connect application components
        self.window.map_widget.viewport.tiles_in_viewport.connect( self.tile_manager.update_viewport )
        self.tile_manager.tiles_changed.connect( self.window.map_widget.set_tiles )
        
        self.window.map_widget.viewport.pan(0, 0)

    def run(self):
        self.window.show()
        self.exec()