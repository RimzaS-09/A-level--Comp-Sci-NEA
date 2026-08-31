import sys
from pathlib import Path

from application import Application
from database_handling.sql_queries import MBTileDatabase
from utils.vector_tile_parsing import vector_tile_pb2
import gzip

from PySide6.QtWidgets import QApplication
from gui.window import MainWindow


ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
MAP_DIR = DATA_DIR / "map"

data = str(MAP_DIR/"OS_Open_Zoomstack.mbtiles")

map_databases = []

for file in (DATA_DIR / "map").iterdir():
    if file.is_file() and str(file).endswith(".mbtiles"):
        map_databases.append(MBTileDatabase(file))

app = QApplication()

window = MainWindow()

app.exec()


"""
def main():
    qt_app = QApplication(sys.argv)

    application = Application()
    application.run()

    sys.exit(qt_app.exec())


if __name__ == "__main__":
    main()
"""