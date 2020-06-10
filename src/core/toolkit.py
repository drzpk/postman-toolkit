from .config import Configuration, ConfigProperty
from .log import Log
from .sqlite.db_manager import DBManager
from .sqlite.migration_manager import MigrationManager
from ..core.model.context import Context
from ..core.service.persistence_manager import PersistenceManager

VERSION = "1.0"

debug = False


class PostmanToolkit:
    context: Context = None

    def __init__(self):
        global debug

        Configuration.initialize()
        _d = ConfigProperty.DEBUG.get_value()
        debug = _d is not None and len(_d) > 0
        Log.debug = debug

        DBManager.initialize(Configuration.config_dir)
        MigrationManager.migrate()

        self.context = Context()
        self.context.environments = PersistenceManager.load_environments()

        # Temporary workaround before environment support is implemented in the frontend
        if self.context.find_environment("default") is None:
            self.context.create_environment("default")
            self.persist_changes()

    def persist_changes(self):
        PersistenceManager.persist_changes(self.context.environments)

    @staticmethod
    def destroy():
        DBManager.destroy()
