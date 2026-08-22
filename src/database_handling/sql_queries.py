import sqlite3
from .connect import SQLConnection

class SQLDatabase:
    def __init__(self, connection: SQLConnection):
        self.connection = connection


class LocationsDatabase(SQLDatabase):
    def __init__(self, connection):
        super().__init__(connection)
 
        
class MBTileDatabase(SQLDatabase):
    def __init__(self, connection):
        super().__init__(connection)

    def get_metadata(self):
        return self.connection.fetch_all("SELECT * FROM metadata")

    def get_tiles_of_zoomlevel(self, zoomlevel):
        return self.connection.fetch_all(f"SELECT * FROM tiles WHERE zoom_level={str(zoomlevel)}")
    
    def get_tile(self, zoom, row, column):
        return self.connection.fetch_one(f"SELECT * FROM tiles WHERE zoom_level={zoom} AND tile_column={column} AND tile_row={row}")