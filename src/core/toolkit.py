from .config import Configuration, ConfigProperty
from .profiles import ProfileConfigLoader, ProfiledConfiguration
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

        self.profiled_configuration = ProfileConfigLoader.load()

        print("loaded configuration:")
        for c in self.profiled_configuration.config_list:
            print("%s: %s" % (c.name, c.value), end="")
            p = c.parent
            while p is not None:
                print(" <-- %s" % p.value)
                p = p.parent

            print()
