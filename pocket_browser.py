import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtWebEngineWidgets import QWebEngineView

from database import Database
from dialog import AddLinkDialog
from ui_features.left_panel_toggle import ToggleButton
from ui_features.left_panel import LeftPanel

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
        self.left_panel = LeftPanel(self.db)
        self.left_panel.add_button.clicked.connect(self.add_link)
        self.left_panel.link_selected.connect(self.on_link_selected)
        self.left_panel.remove_button.clicked.connect(self.delete_link)

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

        """SPLITTER"""
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.left_panel)
        self.splitter.setStretchFactor(0, 1)  # Left: 1x
        self.splitter.setStretchFactor(1, 2)  # Right: 2x (bigger)

        """TOGGLE BUTTON"""
        self.toggle_btn = ToggleButton(self.splitter)

        """RIGHT PANEL WRAPPER: toggle button + browser"""
        right_wrapper_layout = QHBoxLayout()
        right_wrapper_layout.setContentsMargins(0, 0, 0, 0)
        right_wrapper_layout.setSpacing(5)
        right_wrapper_layout.addWidget(self.toggle_btn, alignment=Qt.AlignmentFlag.AlignVCenter)
        right_wrapper_layout.addWidget(right_widget)

        right_wrapper = QWidget()
        right_wrapper.setLayout(right_wrapper_layout)

        self.splitter.addWidget(right_wrapper)

        main_layout.addWidget(self.splitter)
        central_widget.setLayout(main_layout)

    def load_links(self):

        links = self.db.get_all_links()
        self.left_panel.load_links(links)

    def on_link_selected(self, link):
        self.current_link = link
        self.browser.load(QUrl(link["url"]))

    def add_link(self):

        dialog = AddLinkDialog(self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            result = dialog.get_result()
            if result:
                self.db.add_link(result["title"], result["url"])
                self.left_panel.load_links(self.db.get_all_links())
                QMessageBox.information(self, "Success", "Link Added!")

    def delete_link(self):

        current = self.left_panel.current_link

        if not current:
            QMessageBox.warning(self, "Warning", "Please select a link!")
            return

        reply = QMessageBox.question(
            self,
            "Warning",
            f"Do you really want to remove '{current['title']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_link(current['id'])
            self.current_link = None
            self.left_panel.load_links(self.db.get_all_links())
            QMessageBox.information(self, "Deleted", "Link deleted!")


def main():
    app = QApplication(sys.argv)
    window = PocketBrowser()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()