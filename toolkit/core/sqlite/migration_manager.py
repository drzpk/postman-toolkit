import os
import re
import time
import datetime
import sqlite3
import math
import importlib.resources as pkg_resources

from .db_manager import DBManager
from ..log import Log
from . import migrations


class MigrationFile:
    number: int
    name: str
    content: str

    def __init__(self, migration_filename):
        pattern = re.compile("^(\\d+)\\.\\s?(.*)\\.sql$")
        result = re.match(pattern, migration_filename)
        if result is None:
            raise Exception("Migration file {} doesn't conform to the file name requirements".format(migration_filename))

        self.number = int(result.group(1))
        self.name = result.group(2)
        self.content = pkg_resources.read_text(migrations, migration_filename)


class MigrationManager:
    _migrations: [MigrationFile]
    _migration_file_names = [  # todo need a better mechanism for that shit
        "0. Versions.sql",
        "1. Model.sql"
    ]

    @staticmethod
    def migrate():
        db = DBManager.db()
        MigrationManager._load_migration_files()
        MigrationManager._create_migration_table(db)
        MigrationManager._check_for_failed_migrations(db)
        MigrationManager._execute_missing_migrations(db)

    @staticmethod
    def _create_migration_table(db):
        c = db.cursor()
        c.execute("select 1 from sqlite_master where type = 'table' and name = 'schema_versions'")
        result = c.fetchone()
        c.close()
        if result is not None:
            return

        Log.i("Schema version table doesn't exist, creating")
        if len(MigrationManager._migrations) == 0:
            raise Exception("Base migration wasn't found")
        MigrationManager._execute_migration(db, MigrationManager._migrations[0])

    @staticmethod
    def _check_for_failed_migrations(db):
        c = db.cursor()
        c.execute("select id, name from schema_versions where success = 0")
        failed = c.fetchone()
        c.close()

        if failed is not None:
            raise Exception("Database contains a failed migration: {}. {}".format(failed[0], failed[1]))

    @staticmethod
    def _execute_missing_migrations(db):
        existing = [x[0] for x in db.execute("select id from schema_versions")]

        for m in MigrationManager._migrations:
            if m.number not in existing:
                MigrationManager._execute_migration(db, m)

    @staticmethod
    def _load_migration_files():
        migrations = map(lambda x: MigrationFile(x), MigrationManager._migration_file_names)
        migrations = sorted(migrations, key=lambda x: x.number)

        numbers = []
        for m in migrations:
            if m.number in numbers:
                raise Exception(
                    "Error while loading migration {}: Migration with number {} already exists".format(m.name,
                                                                                                       m.number))

        MigrationManager._migrations = migrations

    @staticmethod
    def _execute_migration(db, migration):
        Log.i("Executing migration {}. {}".format(migration.number, migration.name))

        exc = None
        statements = MigrationManager._split_statements(migration.content)
        start = time.time()
        try:
            for statement in statements:
                MigrationManager._execute_statement(db, statement)
        except sqlite3.OperationalError as e:
            Log.e("Error while executing migration {}. {}".format(migration.number, migration.name))
            exc = e
        finally:
            end = time.time()

        execution_time = math.floor((end - start) * 1000)
        MigrationManager._save_migration_status(db, migration, execution_time, exc is None)

        if exc is not None:
            raise exc

    @staticmethod
    def _split_statements(content: str) -> [str]:
        return list(filter(lambda x: not not x.strip(), content.split("\n\n")))

    @staticmethod
    def _execute_statement(db, content):
        c = db.cursor()
        exc = None

        try:
            c.execute(content)
        except sqlite3.OperationalError as e:
            exc = e
        finally:
            c.close()

        if exc is not None:
            raise exc

    @staticmethod
    def _save_migration_status(db, migration, execution_time, result):
        c = db.cursor()
        payload = (migration.number, migration.name, str(datetime.datetime.today()), execution_time, 1 if result else 0)
        c.execute("insert into schema_versions (id, name, created_at, execution_time, success) values (?, ?, ?, ?, ?)",
                  payload)
        db.commit()
        c.close()
