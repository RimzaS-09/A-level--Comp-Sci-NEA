import sqlite3
import threading

class SQLConnection():
    """
    Provides a thin, safe wrapper around the SQL Connection class.
    Mostly used to prevent unwanted changes to the file, if I want it read only
    """

    def __init__(self, file_path: str, read_only: bool = False):
        self._file_path = file_path
        self._read_only = read_only
        
        # threading.local() returns a local bound container to hold stuff in
        # so, for example, self.local.connection, if defined in thread 1, will not carry over
        # into thread 2, and will be treated as if it doesn't exist. 2 Threads can therefore
        # have different values for the same object
        self._local = threading.local() 
            


    def get_file_path(self):
        return self._file_path
    
    def _create_connection(self):
        connection = sqlite3.connect(self._file_path)
        
        if self._read_only:
            connection.cursor().execute("PRAGMA query_only = ON")
            
        return connection

    def _get_threaded_cursor(self):
        """
        Since I'm gonna access the same database via multiple threads,
        It'll be cool to get a thread-local connection/cursor
        This'll do that for me.
        """
        
        # First, Check if we've already made a thread-local connection
        connection = getattr(self._local, "connection", None)
        
        if not connection:
            connection = self._create_connection()
            self._local.connection = connection
        
        return connection.cursor()
    
    def fetch_all(self, command: str, params=()):
        cursor = self._get_threaded_cursor()

        return cursor.execute(command, params).fetchall()

    def fetch_one(self, command: str, params=()):
        cursor = self._get_threaded_cursor()

        return cursor.execute(command, params).fetchone()

    def close_current_thread(self):
        """
        Close the connection belonging to
        the thread calling this method.
        """

        connection = getattr(
            self._local,
            "connection",
            None
        )

        if connection is not None:
            connection.close()

            del self._local.connection
        
        
        
        
        

