import sqlite3
from utils.vector_tile_parsing import vector_tile_pb2
import gzip

def get_metadata (connection):
    cursor = connection.cursor()
    output = cursor.execute("SELECT value FROM metadata WHERE name='maxzoom';")
    
    res = output.fetchall()

    for result in res:
        print(result, "\n")

def get_first_level (connection):
    cursor = connection.cursor()
    output = cursor.execute("SELECT tile_data FROM tiles WHERE zoom_level=10;")
    
    res = output.fetchall()

    return res

if __name__ == "__main__":
    print("Hello world!\n")
    
    connection = sqlite3.connect("data/map/OS_Open_Zoomstack.mbtiles")
    #connection = sqlite3.connect("data/test/mbtiles_vt.mbtiles")

    get_metadata(connection)
    length = len(get_first_level(connection))
    data = get_first_level(connection)[2457][0]

    my_thing = vector_tile_pb2.Tile()


    my_thing.ParseFromString(gzip.decompress(data))

    print(my_thing.layers[5])
    print()
    