"""
This file serves the purpose of:

1. Allowing the user to input locations for a route via the routing dialog
2. Disambiguate between locations, should more than 1 location share the same name (TODO)
"""

import math

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QVBoxLayout,
    QLineEdit,
    QFormLayout,
    QToolButton,
    QGridLayout,
    QCompleter,
    QWidget,
    QListWidget,
    QTableWidget,
    QHeaderView,
    QLabel,
    QTableWidgetItem
)
from PySide6.QtCore import Qt, Slot, Signal, QObject


from models import Graph, Node, Route, MultiRoute
from utils.errors.errors import LocationNotFoundError, RouteNotFoundError, Error
from pathfinding.dijkstra import Djikstra




def format_distance(raw_metres, units="metric") -> str:
    truncated_dist = math.trunc(raw_metres)
    
    if units == "metric":
        # I.e, it's over 1km
        if truncated_dist >= 1000:
            km_dist = truncated_dist / 1000
            return_str = f"{km_dist:.2f} km"
        else:
            return_str = f"{truncated_dist} m"
    else:
        #TODO
        return_str = "? miles"
    
    
    return return_str



class RouteInputDialog(QDialog):
    def __init__(self, parent, names):
        super().__init__(parent)

        self.setWindowTitle("Create a New route")
        self.setMinimumWidth(360)

        self._start = QLineEdit()
        self._start.setPlaceholderText("e.g. Ilford")

        self._end = QLineEdit()
        self._end.setPlaceholderText("e.g. Wanstead flats")

        self._swap = QToolButton()
        self._swap.setText("Swap order")
        self._swap.setToolTip("Swap start and destination")
        self._swap.clicked.connect(self._swap_points)

        grid = QGridLayout()
        grid.addWidget(QLabel("From:"), 0, 0)
        grid.addWidget(self._start,     0, 1)
        grid.addWidget(QLabel("To:"),   1, 0)
        grid.addWidget(self._end,       1, 1)
        grid.addWidget(self._swap,      0, 2, 2, 1)
        grid.setColumnStretch(1, 1)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(grid)
        layout.addWidget(buttons)
        
        
        completer = QCompleter(names, self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        completer.setMaxVisibleItems(8)

        self._start.setCompleter(completer)
        self._end.setCompleter(completer)

    def get_points(self) -> tuple[str, str]:
        return (self._start.text(), self._end.text())
    
    def _swap_points(self):
        start, end = self._start.text(), self._end.text()
        self._start.setText(end)
        self._end.setText(start)

"""
class RouteDisambiguation(QDialog):
    
    Dialog that will pop up in case multiple routes have the same name.
    

    def __init__(self, parent, locations: list[Node]) -> None:
        super().__init__(parent)
        
    def choose_one(self):
        pass
     
"""
# Most important settlement first. Unknown types (e.g. National Park) sort last.
IMPORTANCE = {
    "Capital": 0,
    "City": 1,
    "Town": 2,
    "Suburban Area": 3,
    "Village": 4,
    "Hamlet": 5,
}

def _pick_candidate(candidates: list[Node]) -> Node:
    """TEMP until proper disambiguation"""
    return min(candidates, key=lambda node: IMPORTANCE.get(node.get_type(), 9))

class TempRouteDisambiguation(QDialog):
    """
    NOTE: Temporary class for disambiguating between locations, **but not final**.
    This one just orders by settlement size, and gives the longlat for each settlement.
    
    Future revisions will sort them by how close they are to the viewport's current centre, and centre the screen on them when highlighted.
    """

    def __init__(self, parent, locations: list[Node]) -> None:
        super().__init__(parent)

        self._locations = self._remove_duplicates(
            sorted(locations, key=lambda node: IMPORTANCE.get(node.get_type(), 9))
        )
        name = self._locations[0].get_name()

        self.setWindowTitle("Which place did you mean?")
        self.setMinimumSize(380, 320)

        self._list = QListWidget()
        for node in self._locations:
            self._list.addItem(self._describe_location(node))
        self._list.setCurrentRow(0)
        self._list.itemDoubleClicked.connect(self.accept)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"'{name}' matches {len(self._locations)} places. Which did you mean?"))
        layout.addWidget(self._list)
        layout.addWidget(buttons)

    def get_selected_node(self) -> Node:
        return self._locations[self._list.currentRow()]

    def _remove_duplicates(self, locations: list[Node]) -> list[Node]:
        seen = set()
        unique = []
        for node in locations:
            if node.get_world_coords() not in seen:
                seen.add(node.get_world_coords())
                unique.append(node)
        return unique

    def _describe_location(self, node: Node) -> str:
        lon, lat = node.get_longlat()                         # radians
        lat_deg, lon_deg = math.degrees(lat), math.degrees(lon)
        east_west = "E" if lon_deg >= 0 else "W"
        return f"{node.get_name()} ({node.get_type()}), {lat_deg:.2f}°N {abs(lon_deg):.2f}°{east_west}"


class RouteFinder(QObject):
    route_found = Signal(Route)  # The signal would be of the finalised route, for each point on the route.
    route_failed = Signal(Error)
    
    multi_route_found = Signal(MultiRoute)
    
    def __init__(self, parent, graph: Graph) -> None:
        super().__init__()
        self._graph = graph
        self._parent = parent
    
        
    @Slot(str, str)
    def two_point_route_checker(self, from_point: str, to_point: str):
        from_points = self._graph.search_name(from_point)
        to_points = self._graph.search_name(to_point)
        
        if from_points is None:
            err = LocationNotFoundError(f"We couldn't find {from_point} on the map.")
            self.route_failed.emit(err)
            return
        elif to_points is None:
            err = LocationNotFoundError(f"We couldn't find {to_point} on the map.")
            self.route_failed.emit(err)
            return
        
        from_node = self._get_node(from_points)
        to_node = self._get_node(to_points)
        
        if from_node is None or to_node is None:
            return
        
        path = Djikstra(self._graph).find_path( from_node.get_id(), to_node.get_id() )
        
        if path is None:
            err = RouteNotFoundError(f"Couldn't find a route between {from_point} and {to_point}. There probably isn't a road connection between them.")
            self.route_failed.emit(err)
            return
        
        if path.is_empty():
            err = RouteNotFoundError(f"Both {from_point} and {to_point} are on the same place on the map. Can't form a route to and from the same spot, can we?")
            self.route_failed.emit(err)
            return
        
        
        # Everything under this point is pretty dumb code.
        # TODO: create a dedicated parse_route function that does everything under here for modularity.
        
        
        route_nodes = []    # Note that these are both structural nodes connecting roads to roads as well as the actual start/end POI nodes of the route. As ID's
        route_nodes.append(path.peek().get_connecting_nodes()[0])  # For the initial starting point
        
        roads = []
        total = 0.0
        
        while not path.is_empty():
            cur_edge = path.pop()
            route_nodes.append(cur_edge.get_connecting_nodes()[1])
            
            road_length = cur_edge.get_weight()
            road_info = self._graph.get_road(cur_edge.get_road_id())
            
            # Some edges aren't roads themselves, but extensions of existing roads.
            # these'll have their legngth added to the total, but be omitted from being displayed.
            # This if statement filters them out.
            if road_info:
                # Some slimey roads still slip through
                # Check a road against the last entry in the roads list
                if (roads == []) or (roads[-1][1] != road_info[1]):
                    roads.append( (road_info[0], road_info[1], road_length) )

                else:
                    # Testing found that some roads have no number but different names
                    # Road numbers default to None, so are automatically flagged as the same since both are None, None
                    # This filters out the last of them so they don't accidentally merge
                    if (roads[-1][0] != road_info[0]) and (road_info[1] is None):
                        roads.append( (road_info[0], road_info[1], road_length) )
                    else:
                        # Tuples are immutable, so I have to reconstruct the last entry from scratch
                        last_road = roads[-1]
                        last_road_length = roads[-1][2] + road_length
                        roads[-1] = (last_road[0], last_road[1], last_road_length)
            
            total += road_length
            
        
        route_coords = []
        for node_id in route_nodes:
            route_coords.append(self._graph.get_node(node_id).get_world_coords())
        
        
        self.route_found.emit(Route(from_node, to_node, route_coords, roads, total))

            
    def _get_node(self, node_list: list[Node]) -> Node | None:
        if len(node_list) == 1:
            return node_list[0]
        
        choose_node_dialog = TempRouteDisambiguation(self._parent, node_list)   # TODO: To replace
        if choose_node_dialog.exec() != QDialog.DialogCode.Accepted:
            return None
        
        chosen_node = choose_node_dialog.get_selected_node()
        return chosen_node



class DisplayRouteResultDialog(QDialog):
    def __init__(self, parent, route: Route):
        """Displays the final route as a table."""
        super().__init__(parent)
        self.setWindowTitle("Routing results")
        
        # NOTE: Table is zero indexed for both columns and rows here.
        route_table = QTableWidget(parent=self, rowCount=0, columnCount=2)
        # Row count keeps a live reference to the current no. of rows.
        
        
        route_table.setHorizontalHeaderLabels(["Route", "Distance"])
        route_table.verticalHeader().setVisible(False)
        
        # Some table rules to set up before building
        route_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        route_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        route_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        route_table.insertRow(0)
    
        start_point = QTableWidgetItem(route.start_stop.get_name())
        start_point.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        bold_font = start_point.font()
        bold_font.setBold(True)
        start_point.setFont(bold_font)
        route_table.setItem(0, 0, start_point)
        
        start_column = QTableWidgetItem("Start")
        start_column.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        route_table.setItem(0, 1, start_column)
        
        self._add_road_rows(route_table, route)
        
        last_row = route_table.rowCount()
        route_table.insertRow(last_row)
        
        end_point = QTableWidgetItem(route.end_stop.get_name())
        end_point.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        bold_font = end_point.font()
        bold_font.setBold(True)
        end_point.setFont(bold_font)
        route_table.setItem(last_row, 0, end_point)
        
        end_column = QTableWidgetItem("End")
        end_column.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        route_table.setItem(last_row, 1, end_column)
        
        layout = QVBoxLayout(self)
        layout.addWidget(route_table)
    
    def _add_road_rows(self, table: QTableWidget, route: Route):
            for road in route.road_sections:
                row_num = table.rowCount()
                # Either of these values could be none. Guard them to not display a none-value, just in case.
                # Ideally, display both.
                road_name = road[0]
                road_number = road[1]
                
                if road_name is None:
                    road_name = ""
                if road_number is None:
                    road_number = ""
                
                cur_road = road_name + " " + road_number
                cur_dist = road[2]
                
                road_item = QTableWidgetItem(f"Take the {cur_road}")
                road_dist = QTableWidgetItem(format_distance(cur_dist))
                
                road_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                road_dist.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                table.insertRow(row_num)
                table.setItem(row_num, 0, road_item)
                table.setItem(row_num, 1, road_dist)