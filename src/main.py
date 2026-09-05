import sys
from pathlib import Path

from application import Application
from utils.preprocessor import preprocessor

from PySide6.QtWidgets import QApplication





def main():
    application = Application(sys.argv)
    application.run()


if __name__ == "__main__":
    
    print("If you have not yet processed your geodata in data/map/, press 1 to begin preprocessing")
    print("If you've already processed it through this tool, press 2 to launch the app")
    program_purpose = input("Enter: ")
    
    if program_purpose == "1":
        print("\n\n")
        preprocessor.menu_screen()
    else:
        main()
