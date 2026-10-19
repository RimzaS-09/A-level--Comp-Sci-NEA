from PySide6.QtWidgets import QMainWindow, QFileDialog, QDialog
from PySide6.QtCore import Signal, Slot

from utils.errors.errors import Error
from gui.map_widget import MapWidget
from gui.routing import RouteInputDialog, DisplayRouteResultDialog
from gui.dialogs import show_error
from models import Route, MultiRoute

class MainWindow (QMainWindow):
    route_request = Signal(str, str)
    
    def __init__(self, map_centre, location_names):
        super().__init__()
        
        self.location_names = location_names
        
        self.setWindowTitle("A-Level NEA")
        self.setMinimumSize(720, 480)
        
        self.map_widget = MapWidget(map_centre)
        self.setCentralWidget(self.map_widget)
        
        self._route_result_dialog = None
        
        self.create_menu()
        self.show()
    
    def create_menu(self):
        top_menu = self.menuBar()
        file_menu = top_menu.addMenu("File")
        route_menu = top_menu.addMenu("New route")
        
        load_menu = file_menu.addMenu("Load")
        load_map = load_menu.addAction("Load new map", self.load_map)
        
        quit_button = file_menu.addAction("Quit", self.close)
        
        two_stop_route = route_menu.addAction("Two-stop routefinder", self.new_two_stop_button)
        multi_stop_route = route_menu.addAction("Multi-stop routefinder", self.new_multi_stop_button)
        
        top_menu.addSeparator()
        
    def new_two_stop_button(self):
        route_dialog = RouteInputDialog(self, self.location_names)
        route_option = route_dialog.exec()
        if route_option != QDialog.DialogCode.Accepted:
            return 
        points = route_dialog.get_points()
        self.route_request.emit(*points)
        
    def new_multi_stop_button(self):
        route_dialog = RouteInputDialog(self, self.location_names)
        route_dialog.show()
        points = route_dialog.get_points()
        
    def load_map(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("All mbtiles files (*.mbtiles)")
        file_dialog.exec()
        
    @Slot(Route)
    def display_route(self, route: Route):
        """Display both a route, and a blue line connecting the points on the route, on the map"""
        coords = route.coord_points
        self.map_widget.new_route(coords)
        
        if self._route_result_dialog is not None:
            self._route_result_dialog.close()
        self._route_result_dialog = DisplayRouteResultDialog(self, route)
        self._route_result_dialog.show()

    @Slot(MultiRoute)
    def display_multi_route(self, multi_route):
        pass
        

    @Slot(Error)
    def display_error(self, err):
        show_error(self, err)
        
    



        
        
        
        
        