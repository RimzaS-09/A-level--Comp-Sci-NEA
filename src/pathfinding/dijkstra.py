import math

# TODO
from models import Graph, PathfindingAlgorithm, Node, Edge
from utils.general_purpose_datatypes.queue import DynamicPriorityQueue, QueueValue

class Djikstra(PathfindingAlgorithm):
    def __init__(self, graph: Graph) -> None:
        super().__init__(graph)
    
    def find_path(self, start_id: int, target_id: int) -> list[Edge]|None:
        """
        Traditional Dijkstra's algorithm wouldn't be compatible with our current node/edge adjacency list setup, since the time it takes to load them all into an unvisited list would
        be astronomical. to avoid this, basically only store nodes that are proven to touch one of the visited nodes.
        """
        
        # This visited collection in normal dijkstra is a regular list. But a linear search would be pretty slow for a large number of nodes.
        # to avoid this, its currently set as a hashmap. TODO: create an indexed list instead in the future.
        visited = {}
        
        # All of these are keyed by node_id
        # Nodes with a proven shortest distance are stored here
        # Node_id : distance (metres)
        distances = dict()
        
        # Stores the edge that has been taken to get to a given node
        # Slightly different to normal dijkstra, where this would be the previous node instead of edge
        # Node_id : edge
        came_from = dict()
        
        # Ordinary dijkstra has a full unvisited nodes list, but obviously that'd be extremely wasteful for us
        # so this next_nodes list only stores nodes directly connected to any visited nodes.
        next_nodes = DynamicPriorityQueue()
        
        # Define initial values for the starting node
        next_nodes.enqueue(QueueValue(start_id, 0))
        distances[start_id] = 0.0
        
        while next_nodes.get_length() > 0:
            cur_node_id = next_nodes.dequeue()
            if visited.get(cur_node_id, False):
                continue

            visited[cur_node_id] = True
            
            if cur_node_id == target_id:
                return self._trace_path(came_from, target_id)

            cur_node_dist = distances[cur_node_id]
            
            for neighbour_edge in self._graph.get_node(cur_node_id).get_edges():
                neighbour_node = neighbour_edge.get_connecting_nodes()[1]
                if visited.get(neighbour_node, None):
                    continue
                
                neighbour_dist = cur_node_dist + neighbour_edge.get_weight()
                if neighbour_dist < distances.get(neighbour_node, math.inf):
                    distances[neighbour_node] = neighbour_dist
                    came_from[neighbour_node] = neighbour_edge
                    next_nodes.enqueue( QueueValue(neighbour_node, neighbour_dist) )
                
        # If a path wasn't found
        return None    
     
            
            
    # TODO: should return Stack[Edge] instead.
    def _trace_path(self, came_from: dict, target_id: int) -> list[Edge]:
        """
        returns the final path back. Currently in its reverse order,
        but replacing the path variable with a stack in the future should do the trick thanks to LIFO.
        """

        path = []
        
        cur_id = target_id
        while True:
            edge = came_from.get(cur_id, None)
            
            if not edge:
                return path
            
            path.append(edge)
            cur_id = edge.get_connecting_nodes()[0]
            
            