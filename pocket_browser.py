import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtWebEngineWidgets import QWebEngineView

from database import Database
from dialog import AddLinkDialog

class PocketBrowser (QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pocket Browser")
        self.setGeometry(100, 100, 1200, 700)

        self.db = Database()
        self.current_link = None

        self.setup_ui()
        self.load_links()

    def setup_ui(self):

        self.setWindowTitle("Pocket Browser")
        self.setGeometry(100, 100, 1200, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()

        """LEFT PANEL"""
        left_layout = QVBoxLayout()

        #add Button
        add_button = QPushButton("Add Link")
        add_button.clicked.connect(self.add_link)
        left_layout.addWidget(add_button)

        #link list
        self.links_list = QListWidget()
        self.links_list.itemClicked.connect(self.on_link_selected)
        left_layout.addWidget(self.links_list)

        #remove button
        remove_button = QPushButton("Remove Link")
        remove_button.clicked.connect(self.delete_link)
        left_layout.addWidget(remove_button)

        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        left_widget.setMaximumWidth(250)


        """RIGHT PANEL"""
        right_layout = QVBoxLayout()
        self.name_display = QLabel()
        self.url_display = QLabel()
        self.browser = QWebEngineView()
        right_layout.addWidget(self.browser)

        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        """SPLITTER"""
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)      # Left: 1x
        splitter.setStretchFactor(1, 2)      # Right: 2x (bigger)

        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)

    def load_links(self):

        links = self.db.get_all_links()

        for link in links:
            item = QListWidgetItem(link["title"])
            item.setData(Qt.ItemDataRole.UserRole, link)
            self.links_list.addItem(item)

    def on_link_selected(self, item):

        link = item.data(Qt.ItemDataRole.UserRole)

        if link:
            self.current_link = link
            self.name_display.setText(link["title"])
            self.url_display.setText(link["url"])
            self.browser.load(QUrl(link["url"]))

    def add_link(self):

        dialog = AddLinkDialog(self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            result = dialog.get_result()
            if result:
                link = self.db.add_link(result["title"], result["url"])

                item = QListWidgetItem(link["title"])
                item.setData(Qt.ItemDataRole.UserRole, link)
                self.links_list.addItem(item)

                QMessageBox.information(self, "Success", "Link Added!")

    def delete_link(self):

        if not self.current_link:
            QMessageBox.warning(self, "Warning", "Please select a link!")
            return

        reply = QMessageBox.question(
            self,
            "Warning",
            f"Do you really want to remove '{self.current_link['title']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Delete from database
            self.db.delete_link(self.current_link['id'])

            # Remove from UI list
            for i in range(self.links_list.count()):
                item = self.links_list.item(i)
                link = item.data(Qt.ItemDataRole.UserRole)
                if link['id'] == self.current_link['id']:
                    self.links_list.takeItem(i)
                    break

            # Clear display
            self.current_link = None
            self.name_display.setText("")
            self.url_display.setText("")

            # Success feedback
            QMessageBox.information(self, "Deleted", "Link deleted!")


def main():
    app = QApplication(sys.argv)
    window = PocketBrowser()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()