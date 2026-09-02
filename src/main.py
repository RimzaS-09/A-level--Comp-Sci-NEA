import sys
from pathlib import Path

from application import Application
from database_handling.sql_queries import MBTileDatabase
from utils.vector_tile_parsing import vector_tile_pb2

from PySide6.QtWidgets import QApplication
from gui.window import MainWindow





def main():
    qt_app = QApplication(sys.argv)

    application = Application()
    application.run()

    sys.exit(qt_app.exec())


if __name__ == "__main__":
    main()
