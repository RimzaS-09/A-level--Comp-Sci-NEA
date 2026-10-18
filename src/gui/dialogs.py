from PySide6.QtWidgets import QMessageBox, QDialog, QWidget, QDialogButtonBox, QLabel, QVBoxLayout, QMainWindow, QPushButton, QApplication, QStyle

from utils.errors.errors import Error

class PreprocessorDialog(QDialog):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setWindowTitle("Map must be processed")
        self.setWindowIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation))
        layout = QVBoxLayout()
        
        msg_str = """
        Before we can begin creating routes and searching for locations,
        the map data must be preprocessed.\n\n
        Would you like to continue? Otherwise, the program will run without routing.
        """
        
        button = (QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box = QDialogButtonBox(button)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        message = QLabel(msg_str)
        
        layout.addWidget(message)
        layout.addWidget(self.button_box)
        
        self.setLayout(layout)
        
        self.exec()
        
    def exec(self):
        QApplication.beep()
        return super().exec()
        

def show_error(parent, error: Error):
    #QMessageBox.warning(parent, "Error occured", str(error))
    err_box = QMessageBox(QMessageBox.Icon.Warning, "Error occured", error.err_type, QMessageBox.StandardButton.Ok, parent)
    err_box.setInformativeText(error.msg)
    
    err_box.exec()


if __name__ == '__main__':

    class MainWindow(QMainWindow):

        def __init__(self):
            super().__init__()

            self.setWindowTitle("My App")

            button = QPushButton("Press me for a dialog!")
            button.clicked.connect(self.button_clicked)
            self.setCentralWidget(button)

        def button_clicked(self, checked=False):
            """
            result = QMessageBox.question(
                self,
                "Map must be processed",
                "Before we can begin creating routes and searching for locations, "
                "the map data must be preprocessed.\n\n"
                "Would you like to continue? Otherwise, the program will run without routing.",
                QMessageBox.StandardButton.Ok
                | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel
            )
            """
            result = PreprocessorDialog(self)
                    
            if result.result() == QDialog.DialogCode.Accepted:
                print("Success!")
            else:
                show_error(self, Error("yupp"))
                
    app = QApplication()
    window = MainWindow()
    window.show()
    app.exec()