from .config import Configuration, ConfigProperty
from .profiles import ProfileConfigLoader


VERSION = "1.0"


class PostmanToolkit:

    @staticmethod
    def start():
        Configuration.initialize()

        active_profiles = ConfigProperty.ACTIVE_PROFILES.get_value().split(",")
        loader = ProfileConfigLoader(Configuration.profiles_dir, active_profiles)
        loaded = loader.load()

        print("loaded configuration:")
        for c in loaded.config_entries:
            print("%s: %s" % (c.name, c.value), end="")
            p = c.parent
            while p is not None:
                print(" <-- %s" % p.value)
                p = p.parent

            print()
