from enum import Enum
import gzip
import math

from PySide6.QtGui import QImage
from utils.vector_tile_parsing import vector_tile_pb2

"""
The purpose of models.py is to hold commonly used abstractions, e.g. functions and classes, to be used
Throughout the code.
"""


# Constant containing the width/height of 1 tile, in pixels
TILE_SIZE = 256

PI = math.pi





def tms_to_xyz(tms_y, zoom_level):
    xyz_y = (2 ** zoom_level - 1) - tms_y
    
    return xyz_y


def longlat_to_world(zoom: int, long: float, lat: float) -> tuple[float, float]:
    # NOTE: could raise error of type InvalidCoordinateError
    
    normalised_x = (long + PI) / (2 * PI)
    normalised_y = 0.5 - math.log(math.tan( (PI/4) + (lat/2) )) / ( 2 * PI )
    
    world_x = normalised_x * TILE_SIZE * ( 2**zoom )
    world_y = normalised_y * TILE_SIZE * ( 2**zoom )
    
    return (world_x, world_y)

def world_to_longlat(zoom: int, world_x: float, world_y: float) -> tuple[float, float]:
    
    long = ((2 * PI * world_x) / (TILE_SIZE * 2**zoom)) - PI
    
    normalised_lat = world_y / ( TILE_SIZE * (2**zoom) )
    
    lat_step_1 = math.exp( 2*PI * ( 0.5 - normalised_lat ) )
    lat = 2 * ( math.atan( lat_step_1 ) - (PI/4) )
    
    return (long, lat)




# A typedef to shorten a tuple containing tile metadata
# (zoom, column, row)
TileKey = tuple[int, int, int]



class Geometry:
    def __init__(self, coords: list[tuple]) -> None:
        self._coords = coords
        
    def get_points(self):
        return self._coords
    
    def into_world_coords(self, tile_x, tile_y, extent = 4096)  -> list:
        """
        Converts all coordinates into world-based coordinates, using the 256-depth system I made for viewport
        NOTE: tile x and tile y should be in TMS format (i.e, y is the tile_row flipped)
        """

        world_coords = []
        print(self._coords)
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
                
