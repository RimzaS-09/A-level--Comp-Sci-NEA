# TODO
from models import Graph, PathfindingAlgorithm

class Djikstra(PathfindingAlgorithm):
    def __init__(self, graph: Graph) -> None:
        super().__init__()
        self._graph = graph
        
    def find_path(self, point_a: str, point_b: str):
        node_a = self._graph.search_name(point_a)
        node_b = self._graph.search_name(point_b)
        
        visited = []
        
        