import sqlite3
import json
from ast import literal_eval as parser

from .connect import SQLConnection
from models import RawTile

class SQLDatabase:
    def __init__(self, file_path, read_only = False):
        self.connection = SQLConnection(file_path, read_only=read_only)
        
    def close_thread(self):
        self.connection.close_current_thread()


class LocationsDatabase(SQLDatabase):
    def __init__(self, connection):
        super().__init__(connection)
 

class GraphDatabase(SQLDatabase):
    """
    Class used for handling, creating, and processing the GraphDatabase
    """
    
    ### DATABASE TABLES ###
    
    # I've decided to compose my database from 3 different tables:
    #   - nodes
    #   - edges
    #   - roads
    #
    # Using the nodes and edges tables allow for graph traversal.
    # The roads table provides metadata for the edges, allowing for users to see the route
    # that was generated via the pathfinding algorithm.
    #
    # In addition, the nodes have two fields, kind and name, which allow for me to deduce if their structural,
    # i.e, just connectors between roads (which are edges), or
    # Points of Interest (POIs), which is the term GIS software commonly refer to for locations
    # 
    # E.g., London, Seven Kings station, and Heathrow airpost would all be a POI, in this case.
    # A detailed description for the different POIs and the values in the roads table can be found at
    # https://docs.os.uk/os-downloads/products/maps-and-imagery-portfolio/os-open-zoomstack 
    database_tables = [
        """
        CREATE TABLE IF NOT EXISTS nodes (
            id  INTEGER PRIMARY KEY,
            type TEXT,
            name TEXT,
            world_x REAL,
            world_y REAL,
            long    REAL,
            lat     REAL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS edges (
            id INTEGER PRIMARY KEY,
            from_id INTEGER,
            to_id   INTEGER,
            weight REAL,
            edge_type TEXT,
            road_id INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS roads (
            id  INTEGER PRIMARY KEY,
            name    TEXT,
            number  TEXT,
            type    TEXT,
            level   INTEGER
        )
        """
        
        
    ]
    
    
    def __init__(self, file_path, initial_creation = False):
        if initial_creation:
            super().__init__(file_path, read_only=False)
            self.create_tables()
        else:
            super().__init__(file_path, read_only=True)
    
    
    def bulk_insert(self, table_name, table_rows: list[tuple]):
        self.connection.exec_many(f"INSERT INTO {table_name} VALUES()")
    
    
    def commit_changes(self):
        """Changes MUST be commited before finalisation"""
        
        self.connection.commit()    
    
    def create_tables(self):
        for table_create in self.database_tables:
            self.connection.excec_command(table_create)
        
        self.commit_changes()
    
    


class MBTileDatabase(SQLDatabase):
    """
    Container class for MBTile databases (A type of SQL database).
    
    Differs from the parent class slightly, cause it doesn't allow file editing.
    plus, extra functions for MBtile databases specifically
    """
    
    def __init__(self, file_path):
        super().__init__(file_path, read_only=True)

    def get_metadata(self):
        return self.connection.fetch_all("SELECT * FROM metadata")
    
    def get_metadata_item(self, item):
        # For a specific meetadata item

        # NOTE: could raise error type MetadataNotFoundError
        return self.connection.fetch_one("SELECT value FROM metadata WHERE name=?", (item, ))[0]
    
    def get_centre(self):
        # NOTE: could raise error type MetadataNotFoundError
        # NOTE: could raise error type MetadataParseError
        centre = parser(self.connection.fetch_one("SELECT value FROM metadata WHERE name='center'")[0])
        return centre

    def get_layers_as_json(self):
        # NOTE: could raise error type MetadataNotFoundError
        # NOTE: could raise error type JSonParseError
        layers = json.loads(self.connection.fetch_one("SELECT value FROM metadata WHERE name='json'")[0])
        return layers
    
    def get_layers_as_arr(self):
        # NOTE: could raise error type JSonParseError
        # NOTE: could raise error type MetadataNotFoundError
        layer_json = json.loads( self.connection.fetch_one("SELECT value FROM metadata WHERE name='json'")[0] )
        
        layers = []
    
        # NOTE: could raise error type JSonParseError
        for item in layer_json["vector_layers"]:
            layers.append(item["id"])
        
        return layers
        
    def get_tiles_of_zoomlevel(self, zoom) -> list[RawTile]:
        # NOTE: replace this list with LinkedList in the future
        return_val = []
        
        for raw_tile in self.connection.fetch_all(f"SELECT * FROM tiles WHERE zoom_level=?", (zoom,)):
            tile_key = tuple(raw_tile[0:3])
            return_val.append( RawTile(tile_key, raw_tile[3]) )
        
        return return_val
    
    def iter_tiles_of_zoomlevel(self, zoom):
        
        for raw_tile in self.connection.iter_fetch(f"SELECT * FROM tiles WHERE zoom_level=?", (zoom,)):
            tile_key = tuple(raw_tile[0:3])
            yield RawTile(tile_key, raw_tile[3])
            


    def get_tile_range(self, zoom):
        row_min = self.connection.fetch_one("select MIN(tile_row) FROM tiles WHERE zoom_level=?", (zoom,))[0]
        row_max = self.connection.fetch_one("select MAX(tile_row) FROM tiles WHERE zoom_level=?", (zoom,))[0]
        column_min = self.connection.fetch_one("select MIN(tile_column) FROM tiles WHERE zoom_level=?", (zoom,))[0]
        column_max = self.connection.fetch_one("select MAX(tile_column) FROM tiles WHERE zoom_level=?", (zoom,))[0]
        
        return (row_min, row_max, column_min, column_max)
    
    def get_tile(self, zoom, row, column):
        # NOTE: could raise error type TileNotFoundError
        # Replace current None impl with exception class
        
        raw_tile = self.connection.fetch_one(f"SELECT * FROM tiles WHERE zoom_level=? AND tile_column=? AND tile_row=?", (zoom, column, row))
        if not raw_tile:
            return raw_tile
        
        tile_key = tuple(raw_tile[0:3])
        return RawTile(tile_key, raw_tile[3])
    
    def num_tiles(self, zoom):
        val = self.connection.fetch_one("SELECT COUNT(*) FROM tiles WHERE zoom_level = ?", (zoom, ))[0]
        return val