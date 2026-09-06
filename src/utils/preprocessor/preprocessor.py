from database_handling.sql_queries import MBTileDatabase, GraphDatabase
from utils.vector_tile_parsing import vector_tile_pb2
from models import RawTile, TileKey, tms_to_xyz, longlat_to_world, world_to_longlat
from database_handling.tile_decoder import DecodedTile

from pathlib import Path
from itertools import pairwise
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





###
###     PREPROCESSING FUNCTIONS
###


# NOTE: This is the mean Earth's radius. Idk how much difference it'll make, but maybe
# Find the mean radius for the section of earth at britain?
EARTH_RADIUS = 6371000



node_id = 1
road_id = 1
edge_id = 1

# Roads in layers aren't persistent throughout layers.
# Instead, the zoomstack connects layers via overlapping their end points.
# to stitch them together, I'll create this dict (NOTE: make Hashtable in future):

node_index = dict()
# Keyed as: (world_x, world_y, level)   'level' here means the road level (i.e is it above or below other roads)
# Value as: node_id


# Road_index uses the same hashtable principle to 1. store roads, and 2. prevent duplicate roads from being inserted
# Lookup the key to check if road_id already exists
road_index = dict()
# Keyed as: (road_name, road_num, road_type, road_level)
# Value as road_id



poi_storage = []
edge_storage = []


def haversine(angle) -> float:
    return ( 1 - math.cos(angle) ) / 2

def arc_haversine(num) -> float:
    angle = math.acos( 1 - (2 * num) )
    length = angle * EARTH_RADIUS
    return length


def calc_weight(edge: tuple):
    
    long_1, lat_1 = world_to_longlat(ZOOM_LEVEL, *edge[0])
    long_2, lat_2 = world_to_longlat(ZOOM_LEVEL, *edge[1])

    delta_long = abs( long_2 - long_1 )
    delta_lat = abs( lat_2 - lat_1 )
    
    return arc_haversine( haversine(delta_lat) + ( ( 1-haversine(delta_lat)-haversine(lat_1 + lat_2) ) * haversine(delta_long) ) )
    

def process_graph(tile: RawTile, graph_db: GraphDatabase):
    global node_index
    global road_index
    
    global node_id
    global road_id
    global edge_id
    
    global poi_storage
    global edge_storage
    
    
    decoded_tile = DecodedTile(tile, layers_to_decode=["roads", "names", "airports", "railwaystations"])
    
    for layer in decoded_tile.layers:
        if layer.name == "roads":
            for feature in layer.features:
                # Convert the dict into a tuple for road attribs
                # dictionarys are too expensive memory wise otherwise

                
                road_attributes = (
                    feature.properties.get("name", None),
                    feature.properties.get("number", None),
                    feature.properties.get("type", None),
                    # feature.properties.get("level", 0)      # Tunnels specifically bug out without a matching level
                )
                
                # Roads without numbers or names are unsearchable, so omit them from the database
                # BUT Tunnels do not have numbers or names, and have to be in the db to avoid severing two parts of the graph
                # So Append them in anyways as structural edges
                #if ( (not road_attributes[0]) or (not road_attributes[1]) ) and (road_attributes[2] != "Tunnels"):
                #    continue
                
                # NOTE: omitted above road filtering lines to avoid severing the network
                # TODO: find some way to link a road with no name to it's parent road_id
                
                if road_attributes[0] or road_attributes[1]:
                    check_road = road_index.get(road_attributes, None)
                    cur_road_id = road_id

                    if check_road is None:
                        road_index[road_attributes] = road_id
                        road_id += 1
                    
                    
                else:
                    cur_road_id = None  # I.e, a purely structural node (e.g, the aforementioned Tunnels)
                
                
                for geometry in feature.geometry:
                    
                    for geom_point in geometry.into_world_coords(decoded_tile.x, decoded_tile.y):
                        
                        check_node = node_index.get(geom_point, None )
                        
                        if not check_node:
                            node_index[geom_point] = node_id #type: ignore
                            node_id += 1

                    for edge in pairwise(geometry.into_world_coords(decoded_tile.x, decoded_tile.y)):
                        edge_storage.append( (edge_id, node_index[edge[0]], node_index[edge[1]], calc_weight(edge), "roads", cur_road_id) )

                            
                
                
        elif layer.name == "names":
            # ALL 'names' layers come in the form of a point geometry in zoomstack
            
            for feature in layer.features:
                if feature.geom_type != 1:
                    raise Exception
                geom_world = feature.geometry[0].into_world_coords(decoded_tile.x, decoded_tile.y)
                print(len(feature.geometry))
                poi_storage.append( (node_id, feature.properties["type"], feature.properties["name1"], geom_world) )
    

    
    
    # To implement: after this, stitch the geometries together between tiles
    # Not yet complete

    
    return


def process_POIs():
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
            