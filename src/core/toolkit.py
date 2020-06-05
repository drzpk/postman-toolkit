import os

from .config import Configuration, ConfigProperty
from .profiles import ProfileConfigLoader, ProfiledConfiguration
from .profiles_order import ProfilesOrder
from .sqlite.db_manager import DBManager
from .sqlite.migration_manager import MigrationManager
from .log import Log

VERSION = "1.0"


debug = False


class PostmanToolkit:
    profiled_configuration: ProfiledConfiguration = None

    def __init__(self):
        global debug

        Configuration.initialize()
        _d = ConfigProperty.DEBUG.get_value()
        debug = _d is not None and len(_d) > 0
        Log.debug = debug

        DBManager.initialize(Configuration.config_dir)
        MigrationManager.migrate()

        profiles_order = ProfilesOrder(os.path.normpath(Configuration.config_dir + "/profiles_order"))
        self.profiled_configuration = ProfileConfigLoader.load(profiles_order)

        print("loaded configuration:")
        for c in self.profiled_configuration.config().values():
            print("%s: %s" % (c.name, c.value), end="")
            p = c.parent
            while p is not None:
                print(" <-- %s" % p.value)
                p = p.parent

            print()

    @staticmethod
    def destroy():
        DBManager.destroy()
