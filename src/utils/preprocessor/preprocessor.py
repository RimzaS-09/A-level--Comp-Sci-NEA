from database_handling.sql_queries import MBTileDatabase, GraphDatabase
from utils.vector_tile_parsing import vector_tile_pb2
from models import RawTile, TileKey
from database_handling.tile_decoder import DecodedTile

from pathlib import Path
import time
import math

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = ROOT_DIR / "data"
GRAPH_DIR = ROOT_DIR / "graph"
GRAPH_DIR.mkdir(parents=True, exist_ok=True)
MAP_DIR = DATA_DIR / "map"


###     Different zoom levels give different levels of detail
###         - level 12: All roads, including minor roads, local roads and small paths e.g. sidestreets
###         - Level 10: Motorways, A-level roads, and B-level Roads
###     I haven't optimised yet for minor roads (level 12), so for the demo, I'll keep it at major roads for now
ZOOM_LEVEL = 10


"""
# preprocessor.py

Purpose: To be called before the app starts, so that the database can be loaded

"""




def menu_screen():
    map_databases: list[MBTileDatabase] = []

    # NOTE: could raise error type FileNotFoundError
    for file in (DATA_DIR / "map").iterdir():
        if file.is_file() and str(file).endswith(".mbtiles"):
            map_databases.append(MBTileDatabase(str(file)))
        
        
    database_to_read = None
    while True:            
        
        print("Compatible MBTiles map databases found in data/map/: ")
        for index, item in enumerate(map_databases):
            print(f"\t{index+1}- {item.connection.get_file_path()}")

        print("\n")
        
        try:
            database_to_read = int(input("Choose a database by its number next to it to preprocess: "))
            database_path = map_databases[database_to_read-1]
        
        except ValueError:
            print("\nInvalid input. Please enter a number only")
            continue
        
        except IndexError:
            print("\nInvalid input. Enter a number that is within the list of databases found")
            continue
        
        else:
            process(database_path)
            break


def progress_bar(progress, total):
    percent = 100 * (progress / float(total))
    bar = '█' * int(percent) + '-' * (100-int(percent))
    print(f"\r[{bar}] {percent:.2f}%", end="\r")








def process_graph(tile: RawTile, graph_db: GraphDatabase):
    decoded_tile = DecodedTile(tile, layers_to_decode=["roads"])
    print(decoded_tile.layers[0].features[0].properties["number"])
    
    # To implement: after this, stitch the geometries together between tiles
    # Not yet complete

    
    return


def process_POIs(tiles: list[RawTile]):
    pass


def process(database: MBTileDatabase) -> None:
    print("Scanning tiles in the database... ")
    count = database.num_tiles(ZOOM_LEVEL)
    cur_count = 0
    
    print(f"\n\nDone scanning tiles in database. {count} tiles were found")
    input("Press enter to begin stage 1 of parsing (Creating the structural graph)...")
    print("\nBeginning graph creation...")
    
    
    graph_db = GraphDatabase( str(GRAPH_DIR / "graph.db"), initial_creation=True)
    
    for tile in database.iter_tiles_of_zoomlevel(ZOOM_LEVEL):
        protobuf_tile = vector_tile_pb2.Tile() # type:ignore
        protobuf_tile.ParseFromString(tile.get_vector_data())
        
        graphable = ["roads"]   # NOTE: extent to ["roads", "rail"] later on for rail compatibility
        has_graphable = False
        
        for layer in protobuf_tile.layers:
            if layer.name in graphable:
                has_graphable = True
        
        if has_graphable:
            process_graph(tile, graph_db)

        cur_count += 1
        
        #progress_bar(cur_count, count)
        
    graph_db.close_thread()
        
    print("\n\nSuccess!!")
            