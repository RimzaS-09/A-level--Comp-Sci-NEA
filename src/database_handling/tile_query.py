from .sql_queries import SQLDatabase

class MBTileDatabase(SQLDatabase):
    def __init__(self, connection):
        super().__init__(connection)

    def get_metadata(self):
        return self.connection.fetch_first("SELECT * FROM metadata")

    def get_tiles_of_zoomlevel(self, zoomlevel):
        return self.connection.fetch_first(f"SELECT * FROM tiles WHERE zoom_level={str(zoomlevel)}")