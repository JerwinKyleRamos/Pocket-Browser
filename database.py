
"Database functions: add link, delete link, load link, save link"

import json
from pathlib import Path
from datetime import datetime

DB_Path = Path.home() / ".pocket_browser"
DB_File = DB_Path / "db.json"
DB_Path.mkdir(parents=True, exist_ok=True)

class Database:

    def __init__(self):
        """ Initialize the database and load existing data"""
        self.db_path = DB_File
        self.data = self.load()
        self._migrate()

    """MIGRATE LINKS"""
    def _migrate(self):
        changed = False
        for link in self.data["links"]:
            if "collection" not in link:
                link["collection"] = "Uncategorized"
                changed = True
            if "order" not in link:
                link["order"] = link["id"]
                changed = True
        if "collections" not in self.data:
            self.data["collections"] = ["Uncategorized"]
            changed = True
        if changed:
            self.save()

    "LOAD LINKS"
    def load(self):
        if self.db_path.exists():
            with open(self.db_path, 'r') as f:
                return json.load(f)
        return{"links": [], "collections": ["Uncategorized"]}

    "SAVE LINKS"
    def save(self):
        with open(self.db_path, 'w') as f:
            json.dump(self.data, f, indent=4)

    "ADD LINKS"
    def add_link(self, title, link, collection="Uncategorized"):

        existing_ids = [l["id"] for l in self.data["links"]]
        new_id = max(existing_ids, default=0) + 1
        link = {
            "id": new_id,
            "title": title,
            "url": link,
            "date": datetime.now().isoformat(),
            "collection": collection,
            "order": new_id,
        }

        self.data["links"].append(link)
        self.save()
        return link

    "DELETE LINKS"
    def delete_link(self, link_id):
        self.data["links"] = [
            l for l in self.data["links"] if l["id"] != link_id
        ]
        self.save()

    "LOAD ALL LINKS"
    def get_all_links(self):
        return self.data["links"]

    "GET LINK BY ID"
    def get_link_by_id(self, link_id):

        for l in self.data["links"]:
            if l["id"] == link_id:
                return l
        return None

    "UPDATE LINKS"
    def update_link(self, link_id, title, url):

        link = self.get_link_by_id(link_id)

        if link:
            if title:
                link["title"] = title
            if url:
                link["url"] = url
            self.save()
            return link
        return None

    def move_link(self, link_id, collection, order):
        link = self.get_link_by_id(link_id)

        if link:
            link["collection"] = collection
            link["order"] = order
            self.save()

    def add_collection(self, collection):
        if collection not in self.data["collections"]:
            self.data["collections"].append(collection)
            self.save()

    def delete_collection(self, collection):
        if collection == "Uncategorized":
            return
        self.data["collections"] = [c for c in self.data["collections"] if c != collection]
        for link in self.data["links"]:
            if link["collection"] == collection:
                link["collection"] = "Uncategorized"
        self.save()

    def get_collections(self):
        return self.data["collections"]




