import os
import sqlite3
from flask import g


class DBManager:
    _base_dir: str

    @staticmethod
    def initialize(base_directory):
        DBManager._base_dir = base_directory

    @staticmethod
    def db():
        db = getattr(g, "_database", None)
        if db is None:
            db_path = os.path.normpath(DBManager._base_dir + "/" + "db.sqlite")
            db = g._database = sqlite3.connect(db_path)
        return db

    @staticmethod
    def destroy():
        DBManager.db().close()
