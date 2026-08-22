from utils.vector_tile_parsing import vector_tile_pb2
from enum import Enum




class Geometry:
    def __init__(self, coords) -> None:
        self.coords = coords
        
    def get_points(self):
        return self.coords

class Point(Geometry):
    def __init__(self, coords) -> None:
        super().__init__(coords)
        


class LineString(Geometry):
    def __init__(self, coords) -> None:
        super().__init__(coords)

class Polygon(Geometry):
    def __init__(self, coords, interior_coords) -> None:
        super().__init__(coords)
        
        self.interior = interior_coords










class Graph():
    pass

class TSP_Algorithm():
    pass


class PathfindingAlgorithm():
    pass                       
                
