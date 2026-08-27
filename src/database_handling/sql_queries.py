import sqlite3
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
    def __init__(self, file_path):
        self.connection = SQLConnection(file_path, read_only=True)

    def get_metadata(self):
        return self.connection.fetch_all("SELECT * FROM metadata")
    
    def get_center(self):
        """Note to self: This returns a string, not a tuple. Parse later"""
        return self.connection.fetch_one("SELECT value FROM metadata WHERE name='center'")

    def get_tiles_of_zoomlevel(self, zoomlevel):
        return self.connection.fetch_all(f"SELECT * FROM tiles WHERE zoom_level=?", (zoomlevel,))
    
    def get_tile(self, zoom, row, column):
        return self.connection.fetch_one(f"SELECT * FROM tiles WHERE zoom_level=? AND tile_column=? AND tile_row=?", (zoom, column, row))
    
    def get_tile_data(self, zoom, row, column):
        return self.connection.fetch_one(f"SELECT tile_data FROM tiles WHERE zoom_level=? AND tile_column=? AND tile_row=?", (zoom, column, row))
    