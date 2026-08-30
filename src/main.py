import sys
from pathlib import Path

from application import Application
from database_handling.sql_queries import MBTileDatabase
from utils.vector_tile_parsing import vector_tile_pb2
import gzip

from PySide6.QtWidgets import QApplication



ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
MAP_DIR = DATA_DIR / "map"

data = str(MAP_DIR/"OS_Open_Zoomstack.mbtiles")

database = MBTileDatabase(data)

data = database.get_tiles_of_zoomlevel(4)
for datapoint in data:
    raw_tile = gzip.decompress(datapoint[3])
    tile = vector_tile_pb2.Tile()
    tile.ParseFromString(raw_tile)

print(tile)


"""
def main():
    qt_app = QApplication(sys.argv)

    application = Application()
    application.run()

    sys.exit(qt_app.exec())


if __name__ == "__main__":
    main()
"""