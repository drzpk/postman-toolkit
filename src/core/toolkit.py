from .config import Configuration, ConfigProperty
from .profiles import ProfileConfigLoader
from .globals import Globals
from .log import Log
from ..web.web import run_web


VERSION = "1.0"


debug = False


class PostmanToolkit:

    @staticmethod
    def start():
        global debug

        Configuration.initialize()
        _d = ConfigProperty.DEBUG.get_value()
        debug = _d is not None and len(_d) > 0
        Log.debug = debug

        active_profiles = ConfigProperty.ACTIVE_PROFILES.get_value().split(",")
        loader = ProfileConfigLoader(Configuration.profiles_dir, active_profiles)
        Globals.profiled_configuration = loader.load()

        print("loaded configuration:")
        for c in Globals.profiled_configuration.config_list:
            print("%s: %s" % (c.name, c.value), end="")
            p = c.parent
            while p is not None:
                print(" <-- %s" % p.value)
                p = p.parent

            print()

        run_web()
