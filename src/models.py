from __future__ import annotations
from enum import Enum
import gzip
import math


from PySide6.QtGui import QImage
from utils.vector_tile_parsing import vector_tile_pb2

# Temp fix for circular import
import database_handling

"""
The purpose of models.py is to hold commonly used abstractions, e.g. functions and classes, to be used
Throughout the code.


TODO: A lot of my earlier code isn't fully updated to use these, new, general_purpose functions. Replace them in final refactoring.
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



def get_tile_xyz(world_x, world_y):
    
    tile_x = math.floor(world_x / TILE_SIZE)
    tile_y = math.floor(world_y / TILE_SIZE)
    
    return (tile_x, tile_y)



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



class POI():
    def __init__(self, node_id, type, name, world_coords) -> None:
        self._node_id = node_id
        self._type = type
        self._name = name
        self._world_coords = world_coords
    
    def to_tuple(self):
        return (self._node_id, self._type, self._name, *self._world_coords)
    
    def get_id(self):
        return self._node_id
    
    def get_type(self):
        return self._type
    
    def get_name(self):
        return self._name
    
    def get_coords(self):
        return self._world_coords








        

class Node():
    def __init__(self, id: int, type: str,  name: str, world_coords: tuple[float, float], longlat: tuple[float, float]) -> None:
        self._id = id
        self._type = type
        self._name = name
        self._world_coords = world_coords
        self._longlat = longlat
        self._connected_edges = []
    
    
    # Getters and setters:
    def get_id(self):
        return self._id
    
    def get_type(self):
        return self._type
    
    def get_name(self):
        return self._name
    
    def get_world_coords(self):
        return self._world_coords
    
    def get_longlat(self):
        return self._longlat
    
    
    def append_edge(self, edge: Edge):
        self._connected_edges.append(edge)
        
    def get_edges(self):
        return self._connected_edges


class Edge():
    def __init__(self, id: int, from_id: int, to_id: int, weight: float, edge_type: str, road_id: int) -> None:
        self._id = id
        self._from_id = from_id
        self._to_id = to_id
        self._weight = weight
        self._edge_type = edge_type
        self._road_id = road_id
        
    ## Getters and setters ##
    
    def get_id(self):
        return self._id
    
    def get_connecting_nodes(self):
        return (self._from_id, self._to_id)
    
    def get_weight(self):
        return self._weight
    
    def get_edge_type(self):
        return self._edge_type
    
    def get_road_id(self):
        return self._road_id


class Graph:
    # TODO: I had to circumnavigate the sql_queries circlular import here. replace once a proper fix is made.
    def __init__(self, database: database_handling.sql_queries.GraphDatabase) -> None:
        self._database = database
        self.construct_node_and_name_hashtable()
        self.construct_road_hashtable()
        self.construct_adjacency_list()

    # TODO: replace with my own hashtable
    def construct_node_and_name_hashtable(self):
        self._node_table: dict[int, Node] = dict()
        self._name_table: dict[str, list[Node]] = dict()
        
        for node in self._database.iter_load_row("nodes"):
            id = node[0]
            type = node[1]
            name = node[2]
            world_coords = (node[3],  node[4])
            longlat = (node[5], node[6])
            
            node = Node(id, type, name, world_coords, longlat)
            
            self._node_table[id] = node
            
            
            if name is not None:
                name = name.lower()
                check = self._name_table.get(name, None)
                if check is None:
                    self._name_table[name] = [node]
                else:
                    self._name_table[name].append(node)
    
    def construct_road_hashtable(self):
        self._road_table = dict()
        
        for road in self._database.iter_load_row("roads"):
            id = road[0]
            name = road[1]
            number = road[2]
            type = road[3]
            
            self._road_table[id] = (name, number, type)
    
    # This is a two-way adjacency list
    # Bit inefficient, TODO: find optimisations
    def construct_adjacency_list(self):
        for row in self._database.iter_load_row("edges"):
            id = row[0]
            from_id = row[1]
            to_id = row[2]
            weight = row[3]
            edge_type = row[4]
            road_id = row[5]
            
            edge1 = Edge(id, from_id, to_id, weight, edge_type, road_id)
            edge2 = Edge(id, to_id, from_id, weight, edge_type, road_id)
            
            self._node_table[from_id].append_edge(edge1)
            self._node_table[to_id].append_edge(edge2)
            
    
    def get_node(self, id: int):
        return self._node_table.get(id, None)
    
    def search_name(self, name: str):
        name = name.lower()    
        return self._name_table.get(name, None)
    
    # heuristics-based algorithms dont work with haversine (circular) lengths, so calc world_coord distance here
    # TODO: implement
    def calc_straight_line_dist(self, node1, node2):
        pass
    
    
            
            


class TSP_Algorithm():
    pass



class PathfindingAlgorithm():
    def __init__(self) -> None:
        pass   
                
