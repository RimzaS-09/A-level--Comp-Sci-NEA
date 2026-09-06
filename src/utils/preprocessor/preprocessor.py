from database_handling.sql_queries import MBTileDatabase, GraphDatabase
from utils.vector_tile_parsing import vector_tile_pb2
from models import RawTile, TileKey, tms_to_xyz, longlat_to_world, world_to_longlat, get_tile_xyz, POI
from database_handling.tile_decoder import DecodedTile

from pathlib import Path
from itertools import pairwise
import time
import math

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = ROOT_DIR / "data"
GRAPH_DIR = DATA_DIR / "graph"
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
# Keyed as: (world_x, world_y)
# Value as: node_id


# Road_index uses the same hashtable principle to 1. store roads, and 2. prevent duplicate roads from being inserted
# Lookup the key to check if road_id already exists
road_index = dict()
# Keyed as: (road_name, road_num, road_type)
# Value as road_id


# Stored as tuple of: node_id, type, name1, (world_x, world_y))
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


def create_bucket(world_x, world_y, bucket_size):
    
    tile_x = math.floor(world_x / bucket_size)
    tile_y = math.floor(world_y / bucket_size)
    
    return (tile_x, tile_y)



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
                    cur_road_id = road_index.get(road_attributes, None)

                    if cur_road_id is None:
                        road_index[road_attributes] = road_id
                        cur_road_id = road_id
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
                        edge_id += 1

                            
                
                
        elif layer.name == "names":
            # ALL 'names' layers come in the form of a point geometry in zoomstack
            
            for feature in layer.features:
                if feature.properties["type"] == "Country":
                    continue
                geom_world = feature.geometry[0].into_world_coords(decoded_tile.x, decoded_tile.y)
                
                #poi = POI()
                poi_storage.append( (node_id, feature.properties["type"], feature.properties["name1"], *geom_world) )
                node_id += 1
    return


def process_POIs():
    global edge_id
    global edge_storage
    bucket_size = 8
    
    # Key: the x and y of a tile (in XYZ)
    # Value: A list of node_ids that are in that tile
    tile_nodes =  dict()
    
    for key in node_index.keys():
        tile_xyz = create_bucket(*key, bucket_size)
        
        if not tile_nodes.get(tile_xyz, None):
            tile_nodes[tile_xyz] = [ key ]
        else:
            tile_nodes[tile_xyz].append(key)
    
    count = 0
    total_count = len(poi_storage)
    
    for poi in poi_storage:
        closest_node_coord = None
        closest_node_dist = None
        poi_tile = create_bucket(poi[3][0], poi[3][1], bucket_size)
        
        for x in range(poi_tile[0] - 40, poi_tile[0] + 41):
            for y in range(poi_tile[1] - 40, poi_tile[1] + 41):
                struct_nodes_coords = tile_nodes.get((x, y), None)
                
                if not struct_nodes_coords:
                    continue
                
                for struct_node_coord in struct_nodes_coords:         
                    dist = math.dist(struct_node_coord, (poi[3][0], poi[3][1]))
                    
                    if closest_node_coord is None:
                        closest_node_dist = dist
                        closest_node_coord = struct_node_coord
                    else:
                        if dist < closest_node_dist :
                            closest_node_dist = dist
                            closest_node_coord = struct_node_coord
        
        closest_node = node_index[closest_node_coord]
        edge_storage.append( (edge_id, closest_node, poi[0], calc_weight( (closest_node_coord, poi[3]) ), "structural", None ))
        edge_id += 1
        
        
        progress_bar(count, total_count)
        count += 1


def load_into_database(database: GraphDatabase):
    # First, load the edges
    database.bulk_insert_edges(edge_storage)
    
    nodes = []
    for items in node_index.items():
        longlat = world_to_longlat(ZOOM_LEVEL, *items[0])
        nodes.append( (items[1], "structural", None, *items[0], *longlat) )
        
    database.bulk_insert_nodes(nodes)
    
    nodes = []
    for items in poi_storage:
        # node_id, type, name1, (world_x, world_y))
        
        longlat = world_to_longlat(ZOOM_LEVEL, *items[3])
        nodes.append( (*items[0:3], *items[3], *longlat)  )
    
    database.bulk_insert_nodes(nodes)
    
    # road_index - (road_name, road_num, road_type) : road_id
    # Must insert id, name, num, type in that order
    roads = []
    
    for items in road_index.items():
        roads.append( (items[1], *items[0]) )
    
    database.bulk_insert_roads(roads)
      


def process(database: MBTileDatabase) -> None:
    print("Scanning tiles in the database... ")
    count = database.num_tiles(ZOOM_LEVEL)
    cur_count = 0
    
    print(f"\n\nDone scanning tiles in database. {count} tiles were found")
    input("Press enter to begin stage 1 of preprocessing (Parsing & Creating the structural graph)...")
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
        
        progress_bar(cur_count, count)
    
    print("\n...Success!")
    input("Press enter to being stage 2 of preprocessing (attaching locations to the graph) ...")
    print("\nAdding the locations to the graph nodes...")
    
    process_POIs()
    print("\n...Success!")
    input("Press enter to being stage 3 of preprocessing (Final insertions into the local database) ...")
    print("\nAdding to the database...")
    
    load_into_database(graph_db)    
    graph_db.close_thread()

    
        
    print("\n\nSuccess!!")
            