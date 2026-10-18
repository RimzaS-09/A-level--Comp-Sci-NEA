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
)

from PySide6.QtCore import Qt

from models import Graph, Node

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