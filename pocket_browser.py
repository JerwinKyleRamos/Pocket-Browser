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

        self.left_widget = QWidget()
        self.left_widget.setLayout(left_layout)
        self.left_widget.setMaximumWidth(250)
        self.left_widget.setMinimumWidth(0)

        """RIGHT PANEL"""
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self.name_display = QLabel()
        self.url_display = QLabel()
        self.browser = QWebEngineView()
        right_layout.addWidget(self.browser)

        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        """TOGGLE BUTTON"""
        self.toggle_btn = QPushButton("◀")
        self.toggle_btn.setFixedWidth(18)
        self.toggle_btn.setFixedHeight(60)
        self.toggle_btn.setToolTip("Collapse/Expand panel")
        self.toggle_btn.clicked.connect(self.toggle_left_panel)
        self.toggle_btn.setStyleSheet("""
                 QPushButton {
                     background-color: #cccccc;
                     border: none;
                     border-radius: 4px;
                     font-size: 10px;
                     padding: 0px;
                 }
                 QPushButton:hover {
                     background-color: #aaaaaa;
                 }
             """)

        """RIGHT PANEL WRAPPER: toggle button + browser"""
        right_wrapper_layout = QHBoxLayout()
        right_wrapper_layout.setContentsMargins(0, 0, 0, 0)
        right_wrapper_layout.setSpacing(2)
        right_wrapper_layout.addWidget(self.toggle_btn, alignment=Qt.AlignmentFlag.AlignVCenter)
        right_wrapper_layout.addWidget(right_widget)

        right_wrapper = QWidget()
        right_wrapper.setLayout(right_wrapper_layout)

        """SPLITTER"""
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.left_widget)
        self.splitter.addWidget(right_wrapper)
        self.splitter.setStretchFactor(0, 1)      # Left: 1x
        self.splitter.setStretchFactor(1, 2)      # Right: 2x (bigger)

        main_layout.addWidget(self.splitter)
        central_widget.setLayout(main_layout)


    def toggle_left_panel(self):
        sizes = self.splitter.sizes()
        left_size = sizes[0]

        if left_size > 0:
            # Collapse: save current width, set to 0
            self.left_panel_width = left_size
            total = sum(sizes)
            self.splitter.setSizes([0, total])
            self.toggle_btn.setText("▶")
        else:
            # Expand: restore saved width
            total = sum(sizes)
            self.splitter.setSizes([self.left_panel_width, total - self.left_panel_width])
            self.toggle_btn.setText("◀")

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