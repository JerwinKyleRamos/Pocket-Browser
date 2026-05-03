from collections import defaultdict
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *


class LinkListWidget(QListWidget):
    order_changed = pyqtSignal()

    def __init__(self, collection_collection, parent=None):
        super().__init__(parent)
        self.collection_collection = collection_collection
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QListWidget.DragDropMode.DragDrop)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.setStyleSheet("QListWidget { border: none; background: transparent; }")

    def dropEvent(self, event):
        super().dropEvent(event)
        self.order_changed.emit()

    def sizeHint(self):
        count = self.count()
        return QSize(self.width(), count * 28 + 4)


class CollectionGroup(QWidget):
    link_dropped = pyqtSignal()

    def __init__(self, collection, links,  on_delete=None, parent=None):
        super().__init__(parent)
        self.collection = collection
        self.on_delete = on_delete
        self.is_expanded = True

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.setLayout(layout)

        self.header_btn = QPushButton(f"— {collection.upper()}")
        self.header_btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 4px 8px;
                background: #2a2a2a;
                border: none;
                color: #aaaaaa;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover { color: #ffffff; }
        """)
        self.header_btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.header_btn.customContextMenuRequested.connect(self.show_context_menu)
        self.header_btn.clicked.connect(self.toggle)
        layout.addWidget(self.header_btn)

        self.list_widget = LinkListWidget(collection)
        self.list_widget.order_changed.connect(self.link_dropped)
        layout.addWidget(self.list_widget)

        self.load_links(links)

    def show_context_menu(self, pos):
        if self.collection == "Uncategorized":
            return
        menu = QMenu()
        delete_action = menu.addAction("Delete Collection")
        action = menu.exec(self.header_btn.mapToGlobal(pos))
        if action == delete_action and self.on_delete:
            self.on_delete(self.collection)

    def load_links(self, links):
        self.list_widget.clear()
        for link in links:
            item = QListWidgetItem(link["title"])
            item.setData(Qt.ItemDataRole.UserRole, link)
            self.list_widget.addItem(item)
        count = self.list_widget.count()
        self.list_widget.setFixedHeight(max(count * 28 + 4, 28))

    def toggle(self):
        self.is_expanded = not self.is_expanded
        self.list_widget.setVisible(self.is_expanded)
        self.list_widget.setFixedHeight(0 if not self.is_expanded else max(self.list_widget.count() * 28 + 4, 28))
        prefix = "—" if self.is_expanded else "+"
        self.header_btn.setText(f"{prefix} {self.collection.upper()}")


class LeftPanel(QWidget):
    link_selected = pyqtSignal(dict)

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.groups = []
        self._loading = False
        self.current_link = None
        self.setMaximumWidth(250)
        self.setMinimumWidth(0)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        self.setLayout(layout)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search...")
        layout.addWidget(self.search_bar)
        self.search_bar.textChanged.connect(self.filter_links)

        self.add_collection_btn = QPushButton("+ New Collection")
        self.add_collection_btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 4px 8px;
                background: transparent;
                border: none;
                color: #666666;
                font-size: 11px;
            }
            QPushButton:hover { color: #ffffff; }
        """)
        self.add_collection_btn.clicked.connect(self.create_collection)
        layout.addWidget(self.add_collection_btn)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("QScrollArea { border: none; }")

        self.groups_container = QWidget()
        self.groups_layout = QVBoxLayout()
        self.groups_layout.setContentsMargins(0, 0, 0, 0)
        self.groups_layout.setSpacing(0)
        self.groups_layout.addStretch()
        self.groups_container.setLayout(self.groups_layout)
        self.scroll.setWidget(self.groups_container)
        layout.addWidget(self.scroll)

        self.add_button = QPushButton("Add Link")
        self.remove_button = QPushButton("Remove Link")
        layout.addWidget(self.add_button)
        layout.addWidget(self.remove_button)

    def load_links(self, links):
        for g in self.groups:
            g.setParent(None)
        self.groups = []

        grouped = defaultdict(list)
        for link in links:
            grouped[link.get("collection", "Uncategorized")].append(link)

        for col in self.db.get_collections():
            if col not in grouped:
                grouped[col] = []

        # Newest collections first, Uncategorized always last
        sorted_collections = [c for c in reversed(self.db.get_collections()) if c != "Uncategorized"]
        sorted_collections.append("Uncategorized")

        for collection in sorted_collections:
            group_links = grouped.get(collection, [])
            group = CollectionGroup(collection, group_links, on_delete=self.delete_collection)
            group.list_widget.itemClicked.connect(
                lambda item: self._on_item_clicked(item)
            )
            group.link_dropped.connect(lambda g=group: self.on_drop(g))
            self.groups_layout.insertWidget(self.groups_layout.count() - 1, group)
            self.groups.append(group)

        self._loading = False

    def _on_item_clicked(self, item):
        self.current_link = item.data(Qt.ItemDataRole.UserRole)
        self.link_selected.emit(self.current_link)

    def on_drop(self, source_group):
        if self._loading:
            return
        for group in self.groups:
            for i in range(group.list_widget.count()):
                item = group.list_widget.item(i)
                link = item.data(Qt.ItemDataRole.UserRole)
                if link and self.db.get_link_by_id(link["id"]):
                    self.db.move_link(link["id"], group.collection, i)
            group.list_widget.setFixedHeight(max(group.list_widget.count() * 28 + 4, 28))

    def delete_collection(self, collection):
        self.db.delete_collection(collection)
        self.load_links(self.db.get_all_links())

    def create_collection(self):
        collection, ok = QInputDialog.getText(self, "New Collection", "Collection collection:")
        if ok and collection.strip():
            self.db.add_collection(collection.strip())
            self.load_links(self.db.get_all_links())

    def filter_links(self, text):
        for group in self.groups:
            for i in range(group.list_widget.count()):
                item = group.list_widget.item(i)
                item.setHidden(text.lower() not in item.text().lower())