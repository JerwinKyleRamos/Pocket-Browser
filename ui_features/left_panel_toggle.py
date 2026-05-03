from PyQt6.QtWidgets import QPushButton, QSplitter
from PyQt6.QtCore import Qt


class ToggleButton(QPushButton):

    def __init__(self, splitter: QSplitter, default_width: int = 220):
        super().__init__("◀")
        self.splitter = splitter
        self.left_panel_width = default_width

        self.setFixedWidth(18)
        self.setFixedHeight(60)
        self.setToolTip("Collapse/Expand panel")
        self.setStyleSheet("""
            QPushButton {
                background-color: #cccccc;
                border: none;
                border-radius: 4px;
                font-size: 16px;
                padding: 0px;
                color: black;
            }
            QPushButton:hover {
                background-color: #aaaaaa;
            }
        """)

        self.clicked.connect(self.toggle)

    def toggle(self):
        sizes = self.splitter.sizes()
        left_size = sizes[0]

        if left_size > 0:
            self.left_panel_width = left_size
            total = sum(sizes)
            self.splitter.setSizes([0, total])
            self.setText("▶")
        else:
            total = sum(sizes)
            self.splitter.setSizes([self.left_panel_width, total - self.left_panel_width])
            self.setText("◀")