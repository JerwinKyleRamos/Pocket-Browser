from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QWidget, QVBoxLayout, QLineEdit, QPushButton, QListWidget, QListWidgetItem


class LeftPanel(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumWidth(250)
        self.setMinimumWidth(0)

        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        """SEARCH BAR"""
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search")
        left_layout.addWidget(self.search_bar)
        self.search_bar.textChanged.connect(self.filter_links)

        """ADD BUTTON"""
        self.add_button = QPushButton("Add Link")
        left_layout.addWidget(self.add_button)

        """LINK LIST"""
        self.links_list = QListWidget()
        left_layout.addWidget(self.links_list)

        """REMOVE BUTTON"""
        self.remove_button = QPushButton("Remove Link")
        left_layout.addWidget(self.remove_button)

        self.setLayout(left_layout)

    def load_links(self, links):
        self.links_list.clear()

        header = QListWidgetItem("— MY LINKS")
        header.setFlags(Qt.ItemFlag.NoItemFlags)
        header.setForeground(Qt.GlobalColor.gray)
        self.links_list.addItem(header)

        for link in links:
            item = QListWidgetItem("  " + link["title"])
            item.setData(Qt.ItemDataRole.UserRole, link)
            self.links_list.addItem(item)

    def filter_links(self, text):
        for i in range(self.links_list.count()):
            item = self.links_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())

