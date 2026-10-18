from PySide6.QtWidgets import QMainWindow, QFileDialog, QDialog
from gui.map_widget import MapWidget
from gui.routing import RouteInputDialog

class MainWindow (QMainWindow):
    def __init__(self, map_centre, location_names):
        super().__init__()
        
        self.location_names = location_names
        
        self.setWindowTitle("A-Level NEA")
        self.setMinimumSize(720, 480)
        
        self.map_widget = MapWidget(map_centre)
        self.setCentralWidget(self.map_widget)
        
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
        if route_dialog.exec() != QDialog.DialogCode.Accepted:
            return 
        points = route_dialog.get_points()
        
    def new_multi_stop_button(self):
        route_dialog = RouteInputDialog(self, self.location_names)
        route_dialog.show()
        points = route_dialog.get_points()
        
    def load_map(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("All mbtiles files (*.mbtiles)")
        file_dialog.exec()
    



        
        
        
        
        