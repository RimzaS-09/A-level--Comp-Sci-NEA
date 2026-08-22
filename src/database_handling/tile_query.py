from .sql_queries import SQLDatabase
from enum import Enum
from utils.vector_tile_parsing import vector_tile_pb2
from models import *

import gzip
from itertools import batched


###
###     TODO: A lot of important stuff
###             - Make tile geometry decoding more efficient
###             - Make tile cache system
###             - Allow for features to be decoded in bulk
###             - Create a user defined hashmap for storing key-value pairs



    
    
"""
This File handles with any code relating to decoding MapBox Tiles and MapBox Vector Tile data.
"""


def shoelace_area(coords):
    area = 0

    for i in range(len(coords)):
        x1, y1 = coords[i]
        x2, y2 = coords[(i + 1) % len(coords)]

        area += x1 * y2 - x2 * y1

    return area / 2


def parse_tags(tags, keys, values):
    return_val = dict()
    # TODO: make return_val user-defined hashmap
    for key, value in batched(tags, 2):
        return_val[keys[key]] = values[value]
    return return_val


def decode_geometry(raw_geometry, geom_type):
    coordinates = []
    return_geoms = []
    temp_lines = []
    
    parameters = 0
    
    for index, geom_int in enumerate(raw_geometry):
        if parameters == 0:
            # This is when the geometry integer is a command:
            id = geom_int & 0x7
            count = geom_int >> 3
            
            # i.e, a moveto command
            if id == 1:
                parameters = count * 2
                
                if (geom_type == vector_tile_pb2.Tile.GeomType.LINESTRING) and coordinates:
                    return_geoms.append(LineString(coordinates))
                    coordinates = []
                
            #i.e, a lineto command
            elif id == 2:
                parameters = count * 2
            
            # i.e, a closepath command
            elif id == 7:
                coordinates.append(coordinates[0])
                ring = coordinates
                area = shoelace_area(ring)
                
                if (area > 0) and temp_lines:
                    # assume a new exterior ring if so
                    return_geoms.append(Polygon(temp_lines[0], temp_lines[1:]))
                    temp_lines = []
                    # This completes the last polygon that was from the prior iteration
                
                ring.pop()
                temp_lines.append(ring)
                coordinates = []


        else:
            if parameters % 2 == 0:
                dx = ((raw_geometry[index] >> 1) ^ (-(raw_geometry[index] & 1)))
                dy = ((raw_geometry[index + 1] >> 1) ^ (-(raw_geometry[index + 1] & 1)))
                
                if not coordinates:
                    cur_coords = ( dx, dy )
                else:
                    x = coordinates[-1][0] + dx
                    y = coordinates[-1][1] + dy
                    cur_coords = (x, y)
                
                coordinates.append(cur_coords)
            
            parameters -= 1
            continue
    
    
    match geom_type:
        case vector_tile_pb2.Tile.GeomType.POINT:
            for coord in coordinates:
                return_geoms.append(Point(coord))
        
        case vector_tile_pb2.Tile.GeomType.LINESTRING:
            return_geoms.append(LineString(coordinates))
        
        case vector_tile_pb2.Tile.GeomType.POLYGON:
            return_geoms.append(Polygon(temp_lines[0], temp_lines[1:]))
    
    return return_geoms
            
                
                


def decode_feature(raw_feature, keys, values):
    properties = parse_tags(raw_feature.tags, keys, values)
    geometry = decode_geometry(raw_feature.geometry, raw_feature.type)
    
    return Feature(raw_feature.type, geometry, properties)
    

class GeomCommand(Enum):
    """
    An enum used to contain the different command types.
    
    the values of the enum are a tuple, with the first index indicating the 
    """
    
    MOVETO = (1, 2)
    LINETO = (2, 2)
    CLOSEPATH = (7, 0)
    UNKNOWN = -1





class Feature:
    def __init__(self, geom_type, geometry, properties, id=None) -> None:
        self.geom_type = geom_type
        self.geometry = geometry
        self.properties = properties
        self.id = id
        
    
        


class Layer:
    def __init__(self, layer_index, version, name, features, extent, keys, values) -> None:
        self.layer_index = layer_index
        self.version = version
        self.name = name
        self.extent = extent
        
        self.features = []
        
        for feature in features:
            self.features.append(decode_feature(feature, keys, values))





class DecodedTile():
    def __init__(self, zoom_level, tile_column, tile_row, raw_tile):
        self.layers = []
        self.zoom_level = zoom_level
        self.tile_column = tile_column
        self.tile_row = tile_row
        
        self.x = self.tile_column
        self.y = (2 ** self.zoom_level - 1) - self.tile_row
        
        tile_data = vector_tile_pb2.Tile()
        tile_data.ParseFromString(gzip.decompress(raw_tile))
        
        for index, layer in enumerate(tile_data.layers):
            self.layers.append( Layer(index,
                                      layer.version,
                                      layer.name,
                                      layer.features,
                                      layer.extent,
                                      layer.keys,
                                      layer.values
                                      )
                               )
                
        
    
    def parse_geometry_commands(self, geometry):
        commands = []
        i = 0

        parameter_counts = {
            1: 2,  # MoveTo: dX, dY
            2: 2,  # LineTo: dX, dY
            7: 0   # ClosePath: no parameters
        }

        command_names = {
            1: "MOVETO",
            2: "LINETO",
            7: "CLOSEPATH"
        }

        while i < len(geometry):
            command_integer = geometry[i]
            i += 1

            command_id = command_integer & 0x7
            command_count = command_integer >> 3

            if command_id not in command_names:
                raise ValueError(f"Unknown command ID: {command_id}")

            commands.extend([command_names[command_id]] * command_count)

            parameters_to_skip = parameter_counts[command_id] * command_count

            if i + parameters_to_skip > len(geometry):
                raise ValueError("Geometry contains insufficient parameters")

            i += parameters_to_skip

        return commands