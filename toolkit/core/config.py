import os
from enum import Enum
from .parser import Parser
from .log import Log


config_instance = None


class ConfigProperty:
    SERVER_HOST = os.environ["SERVER_HOST"] if "SERVER_HOST" in os.environ else "localhost"
    SERVER_PORT = os.environ["SERVER_PORT"] if "SERVER_PORT" in os.environ else "8881"
    DEBUG = True if "DEBUG" in os.environ else False

    def get_value(self) -> str:
        return config_instance[self.name] if self.name in config_instance else None


class Configuration:
    data_dir = None
    config_dir = None
    profiles_dir = None

    @staticmethod
    def initialize():
        Configuration.data_dir = os.getcwd()
        return

        Configuration.config_dir = os.path.normpath(root_dir + "/config")
        if not os.path.isdir(Configuration.config_dir):
            os.mkdir(Configuration.config_dir)

        Configuration.profiles_dir = os.path.normpath(Configuration.config_dir + "/profiles")
        if not os.path.isdir(Configuration.profiles_dir):
            os.mkdir(Configuration.profiles_dir)

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
            config[m.name] = m.value.default
            f.write("\n# %s\n%s=%s" % (m.value.comment, m.name, m.value.default))
        f.close()
