from PyQt6.QtWidgets import *
from PyQt6.QtCore import *


class AddLinkDialog(QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Add Link")
        self.setGeometry(100, 100, 400, 150)
        self.result = None
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()

        "title"
        self.title_label = QLineEdit()
        self.title_label.setPlaceholderText("Link Name")
        layout.addRow("Name", self.title_label)

        "url"
        self.url_label = QLineEdit()
        self.url_label.setPlaceholderText("URL")
        layout.addRow("URL", self.url_label)


        "buttons"
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("Add Link")
        cancel_btn = QPushButton("Cancel")

        save_btn.clicked.connect(self.save_link)
        cancel_btn.clicked.connect(self.close)

        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addRow(buttons_layout)

        self.setLayout(layout)

        # Focus on title input when dialog opens
        self.title_label.setFocus()

    def save_link(self):

        title = self.title_label.text().strip()
        url = self.url_label.text().strip()

        if not title or not url:
            QMessageBox.warning(self, "Warning", "Please fill all required fields.")
            return

        if not url.startswith("http"):
            url = "https://" + url

        self.result = {"title": title, "url": url}
        self.accept()

    def get_result(self):
        return self.result