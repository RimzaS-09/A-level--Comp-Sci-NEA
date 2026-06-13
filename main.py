import sqlite3
from MbTileUtils import vector_tile_pb2

def get_metadata (connection):
    cursor = connection.cursor()
    output = cursor.execute("SELECT value FROM metadata WHERE name='format';")
    
    res = output.fetchall()

    for result in res:
        print(result, "\n")

if __name__ == "__main__":
    print("Hello world!\n")
    connection = sqlite3.connect("OS_Open_Zoomstack.mbtiles")

    get_metadata(connection)