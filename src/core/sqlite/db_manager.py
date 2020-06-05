import os
import sqlite3
from flask import g


class DBManager:
    db: sqlite3.Connection

    @staticmethod
    def initialize(base_directory):
        db_path = os.path.normpath(base_directory + "/" + "db.sqlite")
        DBManager.db = sqlite3.connect(db_path)

    @staticmethod
    def destroy():
        DBManager.db.close()