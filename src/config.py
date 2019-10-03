import os
from enum import Enum
from .parser import Parser
from .log import Log


config_instance = None


class ConfigEntry:
    default = None
    comment = None

    def __init__(self, default, comment):
        self.default = default
        self.comment = comment


class ConfigProperty(Enum):
    TEST_PROPERTY = ConfigEntry("test value", "test comment")

    def get(self):
        return config_instance[self.name]


class Configuration:
    config_dir = None
    data_dir = None

    @staticmethod
    def initialize():
        current_dir = os.path.dirname(os.path.realpath(__file__))
        root_dir = os.path.normpath(current_dir + "/../")

        Configuration.config_dir = os.path.normpath(root_dir + "/config")
        if not os.path.isdir(Configuration.config_dir):
            os.mkdir(Configuration.config_dir)

        Configuration.data_dir = os.path.normpath(Configuration.config_dir + "/data")
        if not os.path.isdir(Configuration.data_dir):
            os.mkdir(Configuration.data_dir)

        Configuration._load_app_config()

    @staticmethod
    def _load_app_config():
        global config_instance

        config_file = os.path.normpath(Configuration.config_dir + "/config")
        if not os.path.isfile(config_file):
            open(config_file, "a").close()

        parser = Parser(config_file)
        config = parser.parse()
        config_instance = config
        del parser

        # Find missing properties
        missing = []
        for prop in ConfigProperty:
            if prop.name not in config:
                missing.append(prop)
                Log.i("adding missing property %s to config file" % prop.name)

        # Add missing properties to config file
        f = open(config_file, "a")
        for m in missing:
            f.write("\n# %s\n%s=%s" % (m.value.comment, m.name, m.value.default))
        f.close()
