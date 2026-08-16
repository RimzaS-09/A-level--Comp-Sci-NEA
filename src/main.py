import sys
from pathlib import Path
import os
import gzip

from PySide6.QtWidgets import QApplication, QMainWindow, QLabel
from PySide6 import QtWidgets
from PySide6.QtCore import Qt


from gui import window
from database_handling.connect import SQLConnection
from database_handling.tile_query import MBTileDatabase
from utils.vector_tile_parsing import vector_tile_pb2

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"







if __name__ == "__main__":
    n = len(sys.argv)
    args = sys.argv
    
    # i.e., no arguements were passed

    app = QtWidgets.QApplication(sys.argv)
    
    window = window.MainWindow()
    window.create_menu()

    for file in (DATA_DIR / "map").iterdir():
        if file.is_file() and str(file).endswith(".mbtiles"):
            data = MBTileDatabase(SQLConnection(file))
            dataraw = gzip.decompress(data.get_tiles_of_zoomlevel(10)[0][3])
            tile = vector_tile_pb2.Tile()
            tile.ParseFromString(dataraw)
            print(tile.layers[0].features[0].geometry[0])

    window.show()
    
    app.exec()
    