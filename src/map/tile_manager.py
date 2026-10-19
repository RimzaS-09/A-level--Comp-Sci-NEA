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
        
        # TODO: These are temporary caches until I create a dedicated LRU Cache class
        self._cache = {}          # TileKey maps to a RenderedTile
        self._pending = set()     # TileKeys currently being rendered
        self._visible_keys = []
    
    @Slot(RenderedTile)
    def add_tile(self, tile: RenderedTile):
        tile_key = tile.get_tile_key()
        self._cache[tile_key] = tile
        self._pending.remove(tile_key)
        self.tiles_changed.emit([self._cache[key] for key in self._visible_keys if key in self._cache])
        

    @Slot(tuple)
    def update_viewport(self, view_area):
        
        if len(self._cache) > 500:
            self._cache.clear()
        
        
        # NOTE: Both lists can be replaced with linked lists in the future
        tiles_to_render = []

        zoom = view_area[0]
        coord_area = view_area[1]

        threadpool = QThreadPool.globalInstance()

        visible_keys = []
        
        for x in range(int(coord_area[0]), int(coord_area[1]+1)):
            for y in range(int(coord_area[2]), int(coord_area[3] + 1)):
                
                tile_key: TileKey = (zoom, x, y)
                visible_keys.append(tile_key)
                
                tile = self._cache.get(tile_key, None)
                
                if tile is not None or tile_key in self._pending:
                    continue
                
                tile = self.database.get_tile(zoom, y, x)
                if tile:
                    self._pending.add(tile_key)
                    tiles_to_render.append(tile)

        self._visible_keys = visible_keys
        
        
        for tile in tiles_to_render:
            worker = TileWorker(tile)
            worker.signal.finished.connect(self.add_tile)
            threadpool.start(worker)
        
        self.tiles_changed.emit([self._cache[key] for key in self._visible_keys if key in self._cache])