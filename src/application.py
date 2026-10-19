from PySide6.QtWidgets import QApplication

from pathlib import Path

from models import Graph
from gui.window import MainWindow
from gui.routing import RouteFinder
from database_handling.sql_queries import MBTileDatabase, GraphDatabase
from map.tile_manager import TileManager


ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
MAP_DIR = DATA_DIR / "map"
GRAPH_DIR = DATA_DIR / "graph"

class Application(QApplication):
    """Wrapper around `QApplication`"""
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
        self._graph = Graph(GraphDatabase(str(GRAPH_DIR / "graph.db")))
        
        # NOTE: could raise error type MapDataNotFoundError
        self.tile_manager = TileManager(self.map_databases[0])
        
        map_centre = self.map_databases[0].get_centre()
        self.window = MainWindow(map_centre, self._graph.get_all_poi_names())

        self.route_finder = RouteFinder(self.window, self._graph)
        
        # Connect application components
        self.window.map_widget.viewport.tiles_in_viewport.connect( self.tile_manager.update_viewport )
        self.tile_manager.tiles_changed.connect( self.window.map_widget.set_tiles )
        
        self.window.route_request.connect(self.route_finder.two_point_route_checker)
        
        self.route_finder.route_found.connect(self.window.display_route)
        self.route_finder.route_failed.connect(self.window.display_error)
        
        # Initial pan just to load everything in
        self.window.map_widget.viewport.pan(0, 0)
        
  

    def run(self):
        self.window.show()
        self.exec()