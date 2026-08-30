import sqlite3
import json
from ast import literal_eval as parser

from .connect import SQLConnection

class SQLDatabase:
    def __init__(self, file_path):
        self.connection = SQLConnection(file_path)
        
    def close_thread(self):
        self.connection.close_current_thread()


class LocationsDatabase(SQLDatabase):
    def __init__(self, connection):
        super().__init__(connection)
 
        
class MBTileDatabase(SQLDatabase):
    """
    Container class for MBTile databases (A type of SQL database).
    
    Differs from the parent class slightly, cause it doesn't allow file editing.
    plus, extra functions for MBtile databases specifically
    """
    
    def __init__(self, file_path):
        self.connection = SQLConnection(file_path, read_only=True)

    def get_metadata(self):
        return self.connection.fetch_all("SELECT * FROM metadata")
    
    def get_metadata_item(self, item):
        # For a specific meetadata item
        
        return self.connection.fetch_one("SELECT value FROM metadata WHERE name=?", (item, ))[0]
    
    def get_center(self):
        center = parser(self.connection.fetch_one("SELECT value FROM metadata WHERE name='center'")[0])
        return center

    def get_layers_as_json(self):
        layers = json.loads(self.connection.fetch_one("SELECT value FROM metadata WHERE name='json'")[0])
        return layers
    
    def get_layers_as_arr(self):
        layer_json = json.loads( self.connection.fetch_one("SELECT value FROM metadata WHERE name='json'")[0] )
        
        layers = []
        
        for item in layer_json["vector_layers"]:
            layers.append(item["id"])
        
        return layers
        
    def get_tiles_of_zoomlevel(self, zoomlevel):
        return self.connection.fetch_all(f"SELECT * FROM tiles WHERE zoom_level=?", (zoomlevel,))
    
    def get_tile(self, zoom, row, column):
        return self.connection.fetch_one(f"SELECT * FROM tiles WHERE zoom_level=? AND tile_column=? AND tile_row=?", (zoom, column, row))
    
    def get_tile_data(self, zoom, row, column):
        return self.connection.fetch_one(f"SELECT tile_data FROM tiles WHERE zoom_level=? AND tile_column=? AND tile_row=?", (zoom, column, row))
    