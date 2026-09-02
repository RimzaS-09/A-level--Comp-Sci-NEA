from enum import Enum
import gzip

from PySide6.QtGui import QImage
from utils.vector_tile_parsing import vector_tile_pb2



# A typedef to shorten a tuple containing tile metadata
# (zoom, column, row)
TileKey = tuple[int, int, int]


class Geometry:
    def __init__(self, coords) -> None:
        self.coords = coords
        
    def get_points(self):
        return self.coords

class Point(Geometry):
    def __init__(self, coords) -> None:
        super().__init__(coords)
        


class LineString(Geometry):
    def __init__(self, coords) -> None:
        super().__init__(coords)

class Polygon(Geometry):
    def __init__(self, coords, interior_coords) -> None:
        super().__init__(coords)
        
        self.interior = interior_coords




class RenderedTile:
    """
    Model class For 1 rendered tile
    """
    
    def __init__(self, tile_key: TileKey, raster_image: QImage) -> None:
        self._tile_key = tile_key
        self._image = raster_image
    
    def get_tile_key(self) -> TileKey:
        return self._tile_key
    
    def get_zoom(self) -> int:
        return self._tile_key[0]
    
    def get_coords(self) -> tuple[int, int]:
        return self._tile_key[1:3]
    
    def get_image(self):
        return self._image


class RawTile:
    """
    Model class For 1 rendered tile
    """
    
    def __init__(self, tile_key: TileKey, gzipped_vector_data) -> None:
        self._tile_key = tile_key
        self._vector_data = gzip.decompress(gzipped_vector_data)
    
    def get_tile_key(self) -> TileKey:
        return self._tile_key
    
    def get_zoom(self) -> int:
        return self._tile_key[0]
    
    def get_coords(self) -> tuple[int, int]:
        return self._tile_key[1:3]
    
    def get_vector_data(self):
        return self._vector_data






class Graph():
    pass

class TSP_Algorithm():
    pass


class PathfindingAlgorithm():
    pass                       
                
