from enum import Enum
import gzip

from PySide6.QtGui import QImage
from utils.vector_tile_parsing import vector_tile_pb2



# A typedef to shorten a tuple containing tile metadata
# (zoom, column, row)
TileKey = tuple[int, int, int]

# Constant containing the width/height of 1 tile, in pixels
TILE_SIZE = 256


class Geometry:
    def __init__(self, coords: list[tuple]) -> None:
        self._coords = coords
        
    def get_points(self):
        return self._coords
    
    def into_world_coords(self, tile_x, tile_y, extent = 4096):
        """
        Converts all coordinates into world-based coordinates, using the 256-depth system I made for viewport
        NOTE: tile x and tile y should be in TMS format (i.e, y is the tile_row flipped)
        """

        world_coords = []
        
        for coord in self._coords:
            world_x = tile_x * TILE_SIZE + (coord[0] / extent) * TILE_SIZE
            world_y = tile_y * TILE_SIZE + (coord[1] / extent) * TILE_SIZE
            
            world_coords.append( (world_x, world_y) )

        return world_coords 

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






class Node():
    def __init__(self) -> None:
        pass


class Edges():
    def __init__(self) -> None:
        pass



class TSP_Algorithm():
    pass



class PathfindingAlgorithm():
    pass                       
                
