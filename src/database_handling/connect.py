import sqlite3

class SQLConnection():
    """
    Provides a thin, safe wrapper around the SQL Connection class. 
    """

    def __init__(self, filename):
        self.connection = sqlite3.connect(filename)
        self.cursor = self.connection.cursor()

    def fetch_first(self, command: str):
        self.cursor.execute(command)
        return self.cursor.fetchall()

    def close(self):
        self.connection.close()

