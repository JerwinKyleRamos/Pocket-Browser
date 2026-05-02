
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

    "LOAD LINKS"
    def load(self):
        if self.db_path.exists():
            with open(self.db_path, 'r') as f:
                return json.load(f)
        return{"links": []}

    "SAVE LINKS"
    def save(self):
        with open(self.db_path, 'w') as f:
            json.dump(self.data, f, indent=4)

    "ADD LINKS"
    def add_link(self, title, link):

        existing_ids = [l["id"] for l in self.data["links"]]
        new_id = max(existing_ids, default=0) + 1
        link = {
            "id": new_id,
            "title": title,
            "url": link,
            "date": datetime.now().isoformat()
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


