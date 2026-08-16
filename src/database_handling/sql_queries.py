import sqlite3
from .connect import SQLConnection

class SQLDatabase:
    def __init__(self, connection: SQLConnection):
        self.connection = connection


class LocationsDatabase(SQLDatabase):
    def __init__(self, connection):
        super().__init__(connection)